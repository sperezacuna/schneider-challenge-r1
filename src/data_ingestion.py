import os
import sys
import argparse
import requests
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils import load_config
from xml_utils import xmls_to_df_dict
from constants import ( countries, regions )

def main(args):
  """
  Perform energy data ingestion from ENTSO-E API and store the data in a CSV file.

  :param args: Command-line arguments.
  """
  config = load_config()
  partial_dfs = [] # List to store intermediate DataFrames
  df = pd.DataFrame()
  for country in countries:
    print(f"Ingesting data for country {country}")
    load_dict = get_region_load_df_from_entsoe(
      url=config.get('Common', 'APIUrl'),
      token=config.get('Common', 'APIToken'),
      region=regions[country],
      period_start=config.getint('Ingestion', 'StartDate'),
      period_end=config.getint('Ingestion', 'EndDate')
    )
    gen_dict = get_region_gen_df_from_entsoe(
      url=config.get('Common', 'APIUrl'),
      token=config.get('Common', 'APIToken'),
      region=regions[country],
      period_start=config.getint('Ingestion', 'StartDate'),
      period_end=config.getint('Ingestion', 'EndDate')
    )
    combined_dict = { **load_dict, **gen_dict }
    for type in combined_dict:
      partial_dfs.append((combined_dict[type], country, type))
    
  # Concatenate all intermediate DataFrames
  date_start = min([df.index.min() for df, _, _ in partial_dfs if not df.empty])
  date_end = max([df.index.max() for df, _, _ in partial_dfs if not df.empty])
  df = join_all_dfs(partial_dfs, date_start, date_end)
  df = complete_df(df)
  print("Z")
  print(df)
  save_df(df, filePath=os.path.abspath(args.output_file))

def get_region_load_df_from_entsoe(url, token, region, period_start, period_end):
  params = {
    'securityToken': token, 
    'documentType': 'A65',
    'processType': 'A16',
    'outBiddingZone_Domain': region
  }
  xmls = []
  while (period_start < period_end):
    params['periodStart'] = period_start
    params['periodEnd'] = period_start+100000000 if period_end > period_start+100000000 else period_end
    print(f"\tRequesting load data")
    response = requests.get(url, params=params, headers=None)
    if response.status_code == 200:
      xmls.append(response.text)
    else:
      raise Exception(f"API request failed. Status code: {response.status_code}")
    period_start += 100000000 # Set start date to 1 year later
  return xmls_to_df_dict(xmls, type='load')

def get_region_gen_df_from_entsoe(url, token, region, period_start, period_end):
  params = {
    'securityToken': token, 
    'documentType': 'A75',
    'processType': 'A16',
    'in_Domain': region
  }
  xmls = []
  while (period_start < period_end):
    params['periodStart'] = period_start
    params['periodEnd'] = period_start+100000000 if period_end > period_start+100000000 else period_end
    print(f"\tRequesting generation data")
    response = requests.get(url, params=params, headers=None)
    if response.status_code == 200:
      xmls.append(response.text)
    else:
      raise Exception(f"API request failed. Status code: {response.status_code}")
    period_start += 100000000 # Set start date to 1 year later
  return xmls_to_df_dict(xmls, type='generation')

def join_all_dfs(partial_dfs, date_start, date_end):
  """
  Concatenate all intermediate DataFrames into a single structure.

  :param dfs: List of tuples, each with an intermediate DataFrame and associated country/parameter information.
  :return: Resulting DataFrame.
  """
  full_timestamp_range = pd.date_range(start=date_start, end=date_end, freq='15T')
  for dfi, country, parameter in partial_dfs:
    # Rename columns based on country and parameter information
    new_column_name = f"{country}_{parameter}"
    dfi.rename(columns={'quantity': new_column_name}, inplace=True)
  entire_result = pd.concat([df[[f'{country}_{parameter}']] for df, country, parameter in partial_dfs], axis=1)
  entire_result = entire_result.reindex(full_timestamp_range)
  entire_result['id'] = range(1, len(entire_result) + 1)
  entire_result['Time'] = entire_result.index
  print("X")
  print(entire_result)
  entire_result = entire_result[['Time'] + sorted([col for col in entire_result.columns if col != 'Time'])]
  entire_result.set_index('id', inplace=True)
  print("Y")
  print(entire_result)
  return entire_result

def complete_df(df):
  all_types = ["B{:02d}".format(i) for i in range(1, 25)] + ['load']
  for country in countries:
    for type in all_types:
      if f'{country}_{type}' not in df.columns:
        df[f'{country}_{type}'] = np.nan
  return df[['Time'] + sorted([col for col in df.columns if col != 'Time'])]

def save_df(df, filePath):
  """
  Save the DataFrame to a CSV file.

  :param df: DataFrame to be saved.
  :param filePath: Path of the output CSV file.
  """
  df.to_csv(filePath, index=True)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description='Performs energy data ingestion and stores it in a csv file'
  )
  parser.add_argument(
    '--output_file', '-o', type=str,
    default=os.path.join(os.path.dirname(__file__), '../data/raw_data.csv'),
    help='the path of the file where raw data will be saved [default is data/raw_data.csv]'
  )
  args = parser.parse_args()
  main(args)
