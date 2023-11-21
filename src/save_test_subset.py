import os
import sys
import json
import argparse
import pandas as pd

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def main(args):
  df = load_df(filePath=os.path.abspath(args.input_file))
  if args.size == 0.2:
    print("Using default size of 20% of the whole dataset")
    df = df.tail(int(len(df)*0.2))
  else:
    print(f"Using size {int(args.size)}")
    df = df.tail(int(args.size))
  if args.ground_truth_file != "nil":
    true_labels = [ int(label) for label in df['label'].values ]
    save_predictions(true_labels, output_file=os.path.abspath(args.ground_truth_file))
  if not args.labeled:
    df = df.drop(columns=['label'])
  save_df(df, filePath=os.path.abspath(args.output_file))

def load_df(filePath):
  df = pd.read_csv(filePath, index_col=0)
  df['Time'] = pd.to_datetime(df['Time'])
  numeric_cols = df.columns.difference(['id', 'Time'])
  df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce', downcast='float')
  return df

def save_df(df, filePath):
  df.to_csv(filePath, index=True)

def save_predictions(predictions, output_file):
  try:
    with open(output_file, 'w') as f:
      f.write(json.dumps({
        "target": { i: label for i, label in enumerate(predictions) }
      }))
  except Exception as e:
    print(f"[!] Error saving predictions to {output_file}: {e}.\nMake sure the folder exists. Remember that the current generated model was stored as a pkl file")
    sys.exit(1)

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
    '--ground_truth_file', '-g', type=str,
    default="nil",
    help='the path of the file where the ground truth will be stored [default is nil]'
  )
  parser.add_argument(
    '--size', '-s', type=float,
    default=0.2,
    help='the size of the test subset [default is 20% of the whole dataset]'
  )
  parser.add_argument(
    '--labeled', '-l', action='store_true',
    help='whether the test subset is labeled or not [default is False]'
  )
  args = parser.parse_args()
  main(args)