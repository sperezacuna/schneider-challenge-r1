import os
import sys
import warnings
import argparse
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from constants import (
  countries,
  renewable_energies,
  country_id_map
)

def main(args):
  df = load_df(filePath=os.path.abspath(args.input_file))
  print(df)
  df = clean_data(df)
  df = compute_labels(df)
  save_df(df, filePath=os.path.abspath(args.output_file))

def clean_data(df):
  df = df.interpolate(method='linear')
  df_resampled = df.drop(columns=['id', 'Time'])
  # Assume that the data starts at the beginning of the hour
  df_resampled = df_resampled.groupby(df.index // 4 * 4).agg(lambda group: np.nan if all(group.isna()) else group.mean())
  df_resampled = df_resampled.reset_index(drop=True)
  df_resampled['Time'] = df['Time'].min() + pd.to_timedelta(df_resampled.index, unit='H')
  df_resampled = df_resampled[['Time'] + [col for col in df_resampled.columns if col != 'Time']]
  #df_resampled.interpolate(method='linear', inplace=True)
  return df_resampled

def load_df(filePath):
  df = pd.read_csv(filePath)
  df['Time'] = pd.to_datetime(df['Time'])
  numeric_cols = df.columns.difference(['id', 'Time'])
  df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce', downcast='float')

  return df

def compute_labels(df):
  for country in countries:
    green_energy_columns = [f'{country}_{renewable_energy}' for renewable_energy in renewable_energies]
    country_green_column = f'{country}_green_energy'
    surplus_column = f'{country}_surplus'
    warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)
    df[country_green_column] = df[green_energy_columns].fillna(0).sum(axis=1)
    df[surplus_column] = df[country_green_column] - df[f'{country}_load']
    df = df[df.columns.drop(list(df.filter(like=f'{country}_B')))]

  # Find the column with the maximum surplus for each row and assign the corresponding label
  max_surplus_column = df[[f'{country}_surplus' for country in countries]].idxmax(axis=1)
  df['label'] = max_surplus_column.apply(lambda col_name: country_id_map[col_name.split('_')[0]])
  df['label'] = df['label'].shift(-1)
  df = df.drop(df.index[-1])
  df['label'] = df['label'].astype(int)

  # Delete the temporary columns used in the calculation
  #columns_to_drop = [f'{country}_green_energy' for country in countries] + [f'{country}_surplus' for country in countries]

  #df = df.drop(columns=columns_to_drop)
  return df

def save_df(df, filePath):
  df.to_csv(filePath, index=True)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description='Performs cleaning and homogeneization on ingested data and stores it in a csv file'
  )
  parser.add_argument(
    '--input_file', '-i', type=str,
    default=os.path.join(os.path.dirname(__file__), '../data/raw_data.csv'),
    help='the path of the file where raw data is stored [default is data/raw_data.csv]'
  )
  parser.add_argument(
    '--output_file', '-o', type=str,
    default=os.path.join(os.path.dirname(__file__), '../data/processed_data.csv'),
    help='the path of the file where processed data will be saved [default is data/processed_data.csv]'
  )
  args = parser.parse_args()
  main(args)