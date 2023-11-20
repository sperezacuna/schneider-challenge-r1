import os
import sys
import argparse
import pandas as pd

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def main(args):
  df = load_df(filePath=os.path.abspath(args.input_file))
  if args.size == 0.2:
    print("Using default size of 20% of the whole dataset")
    test_df = df.tail(int(len(df)*0.2))
  else:
    print(f"Generating dataset of size {int(args.size)}")
    test_df = df.tail(int(args.size))
  save_df(test_df, filePath=os.path.abspath(args.output_file))

def load_df(filePath):
  df = pd.read_csv(filePath, index_col=0)
  df['Time'] = pd.to_datetime(df['Time'])
  numeric_cols = df.columns.difference(['id', 'Time'])
  df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce', downcast='float')
  return df

def save_df(df, filePath):
  df.to_csv(filePath, index=True)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description='Performs cleaning and homogeneization on ingested data and stores it in a csv file'
  )
  parser.add_argument(
    '--input_file', '-i', type=str,
    default=os.path.join(os.path.dirname(__file__), '../data/processed_data.csv'),
    help='the path of the file where whole processed data is stored [default is data/processed_data.csv]'
  )
  parser.add_argument(
    '--output_file', '-o', type=str,
    default=os.path.join(os.path.dirname(__file__), '../data/test.csv'),
    help='the path of the file where the test subset will be stored [default is data/test.csv]'
  )
  parser.add_argument(
    '--size', '-s', type=float,
    default=0.2,
    help='the size of the test subset [default is 20% of the whole dataset]'
  )
  args = parser.parse_args()
  main(args)