import os
import sys
import argparse
import datetime
import requests
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils import load_config, inspect_dataframe
from parse_utils import xmls_to_df_dict, jsons_to_df_dict
from constants import countries, regions

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
    params = {
      'period_start': args.start_time,
      'period_end': args.end_time
    }
    if not args.only_entsoe and country == 'UK':
      params['url'] = config.get('Common', 'ElexonAPIUrl')
      load_dict = get_UK_load_df_from_elexon(**params)
      gen_dict  = get_UK_gen_df_from_elexon(**params)
    else:
      params['url'] = config.get('Common', 'ENTSOEAPIUrl')
      params['token'] = config.get('Common', 'ENTSOEAPIToken')
      params['region'] = regions[country]
      load_dict = get_region_load_df_from_entsoe(**params)
      gen_dict  = get_region_gen_df_from_entsoe(**params)
    for type, df in (load_dict | gen_dict).items():
      partial_dfs.append((df, country, type))
    
  print("Concatenating all dataframes")
  date_start = min([df.index.min() for df, _, _ in partial_dfs if not df.empty])
  date_end = max([df.index.max() for df, _, _ in partial_dfs if not df.empty])
  df = join_all_dfs(partial_dfs, date_start, date_end)
  df = complete_df(df)
  print(df)
  save_df(df, filePath=os.path.abspath(args.output_file))
  inspect_dataframe(df, args.output_file) # Monitors csv content

def get_region_load_df_from_entsoe(url, token, region, period_start, period_end):
  params = {
    'securityToken': token, 
    'documentType': 'A65',
    'processType': 'A16',
    'outBiddingZone_Domain': region
  }
  xmls = []
  while (period_start < period_end):
    max_query_period_end = period_start+relativedelta(years=1)
    params['periodStart'] = (period_start).strftime('%Y%m%d%H%M')
    params['periodEnd']   = (max_query_period_end if period_end > max_query_period_end else period_end).strftime('%Y%m%d%H%M')
    print(f"\tRequesting load data from {url} from {params['periodStart']} to {params['periodEnd']}")
    response = requests.get(url, params=params, headers=None)
    if response.status_code == 200:
      xmls.append(response.text)
    else:
      raise Exception(f"API request failed. Status code: {response.status_code}")
    period_start += relativedelta(years=1)
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
    max_query_period_end = period_start+relativedelta(years=1)
    params['periodStart'] = (period_start).strftime('%Y%m%d%H%M')
    params['periodEnd']   = (max_query_period_end if period_end > max_query_period_end else period_end).strftime('%Y%m%d%H%M')
    print(f"\tRequesting generation data from {url} from {params['periodStart']} to {params['periodEnd']}")
    response = requests.get(url, params=params, headers=None)
    if response.status_code == 200:
      xmls.append(response.text)
    else:
      raise Exception(f"API request failed. Status code: {response.status_code}")
    period_start += relativedelta(years=1)
  return xmls_to_df_dict(xmls, type='generation')

def get_UK_load_df_from_elexon(url, period_start, period_end):
  params = {
    'format': 'json'
  }
  jsons = []
  period_end -= relativedelta(days=1) # Just remove the last day, as it is included in the response
  while (period_start < period_end):
    max_query_period_end = period_start+relativedelta(days=28)
    params['settlementDateFrom'] = (period_start).strftime('%Y-%m-%d')
    params['settlementDateTo']   = (max_query_period_end if period_end > max_query_period_end else period_end).strftime('%Y-%m-%d')
    print(f"\tRequesting load data from {url} from {params['settlementDateFrom']} to {params['settlementDateTo']}")
    response = requests.get(f'{url}/demand', params=params, headers=None)
    if response.status_code == 200:
      jsons.append(response.json())
    else:
      raise Exception(f"API request failed. Status code: {response.status_code}")
    period_start += relativedelta(days=28)
  return jsons_to_df_dict(jsons, type='load')

def get_UK_gen_df_from_elexon(url, period_start, period_end):
  params = {
    'includeNegativeGeneration': False,
    'format': 'json'
  }
  jsons = []
  while (period_start < period_end):
    max_query_period_end = period_start+relativedelta(days=14)
    params['startTime'] = (period_start).strftime('%Y-%m-%d')
    params['endTime']   = (max_query_period_end if period_end > max_query_period_end else period_end).strftime('%Y-%m-%d')
    print(f"\tRequesting generation data from {url} from {params['startTime']} to {params['endTime']}")
    response = requests.get(f'{url}/generation/outturn/summary', params=params, headers=None)
    if response.status_code == 200:
      jsons.append(response.json())
    else:
      raise Exception(f"API request failed. Status code: {response.status_code}")
    period_start += relativedelta(days=14)
  return jsons_to_df_dict(jsons, type='generation')

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
  entire_result = pd.concat([entire_result, entire_result.index.to_frame(name='Time')], axis=1)
  entire_result = entire_result.reset_index(drop=True)
  return entire_result

def complete_df(df):
  all_types = ["B{:02d}".format(i) for i in range(1, 25)] + ['load']
  new_columns = []
  for country in countries:
    for type in all_types:
      new_column_name = f'{country}_{type}'
      if new_column_name not in df.columns:
        new_columns.append(pd.Series(name=new_column_name, dtype=np.float64))
  if new_columns:
    df = pd.concat([df] + new_columns, axis=1)

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
    '--start_time', '-s',
    type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'), 
    default=datetime.datetime(2022, 1, 1),
    help='Start time for the data to download, format: YYYY-MM-DD'
  )
  parser.add_argument(
    '--end_time', '-e',
    type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'), 
    default=datetime.datetime(2023, 1, 1),
    help='End time for the data to download, format: YYYY-MM-DD'
  )
  parser.add_argument(
    '--only_entsoe', action='store_true',
    help='Use Elexon API for UK data [default is False]'
  )
  parser.add_argument(
    '--output_file', '-o', type=str,
    default=os.path.join(os.path.dirname(__file__), '../data/raw_data.csv'),
    help='the path of the file where raw data will be saved [default is data/raw_data.csv]'
  )
  args = parser.parse_args()
  main(args)
