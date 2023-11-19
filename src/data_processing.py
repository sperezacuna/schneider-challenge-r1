import os
import sys
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
  df = drop_non_renewable_energy_columns(df)
  df = clean_data(df)
  df = compute_aggregates(df)
  df = drop_renewable_energy_columns(df)
  df = compute_labels(df)
  print(df)
  save_df(df, filePath=os.path.abspath(args.output_file))

def load_df(filePath):
  df = pd.read_csv(filePath, index_col=0)
  df['Time'] = pd.to_datetime(df['Time'])
  numeric_cols = df.columns.difference(['id', 'Time'])
  df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce', downcast='float')
  return df

def clean_data(df):
  # Assume that the data starts at the beginning of an hour and is sampled in 15 minute intervals
  startTime = df['Time'].min()
  df = df.drop(columns=['Time'])

  # Now we can resample the data to 1 hour intervals by averaging the existing values
  df_resampled = df.groupby((df.index) // 4 * 4).agg(lambda group: np.nan if all(group.isna()) else group.mean())
  # Reset the index
  df_resampled = df_resampled.reset_index(drop=True)
  # And recreate the Time column with the new intervals
  df_resampled['Time'] = startTime + pd.to_timedelta(df_resampled.index, unit='H')

  # Reorder the columns so that Time is the first one
  df_resampled = df_resampled[['Time'] + sorted([col for col in df_resampled.columns if col != 'Time'])]

  # Fill all the gaps at the middle, beggining or end of the data with linear interpolation (average of the previous and next values)
  df_resampled.interpolate(method='linear', limit_direction='both', inplace=True)
  # And completely empty series with 0
  df_resampled = df_resampled.fillna(0)

  return df_resampled

def compute_aggregates(df):
  for country in countries:
    green_energy_columns = [f'{country}_{renewable_energy}' for renewable_energy in renewable_energies]
    # Compute the green energy and surplus for each country
    df[f'{country}_green_energy'] = df[green_energy_columns].sum(axis=1)
    df[f'{country}_surplus']      = df[f'{country}_green_energy'] - df[f'{country}_load']
  return df

def drop_renewable_energy_columns(df):
  columns_to_drop = [f'{country}_{renewable_energy}' for country in countries for renewable_energy in renewable_energies]
  return df.drop(columns=columns_to_drop)

def drop_non_renewable_energy_columns(df):
  # non renewable energies are those that start with {country}B?? and are not renewable_energies
  columns_to_drop = [col for country in countries for col in df.columns if col.startswith(f'{country}_B') and col.split('_')[1] not in renewable_energies]
  return df.drop(columns=columns_to_drop)

def compute_labels(df):
  # Find the column with the maximum surplus for each row and assign the corresponding label
  max_surplus_column = df[[f'{country}_surplus' for country in countries]].idxmax(axis=1)
  df['label'] = max_surplus_column.apply(lambda col_name: country_id_map[col_name.split('_')[0]])
  
  # We are predicting the surplus for the next hour, so we need to shift the labels one row up
  df['label'] = df['label'].shift(-1)
  # And drop the last row, which has no label
  df = df.drop(df.index[-1])

  # Convert the label to int
  df['label'] = df['label'].astype(int)

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