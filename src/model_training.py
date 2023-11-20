import os
import sys
import argparse

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from dataset_helpers import DatasetWrapper

def main(args):
  model = load_model(args.model_type)
  dataset = DatasetWrapper(
    df_csv=os.path.abspath(args.input_file),
    batch_size=model.parameters.getint('BatchSize'),
    window_size=model.parameters.getint('WindowSize'),
    countries_in_use=model.parameters.get('CountriesInUse').split(','),
    country_hyperparams=model.parameters.get('CountryHyperparams').split(','),
    phase="training"
  )
  model.train(dataset)
  model.save(os.path.abspath(args.model_file))

def load_model(model_type):
  if model_type == "recurrentLSTM":
    from models import RecurrentLSTMModel
    return RecurrentLSTMModel()
  else:
    print("[!] Invalid model type")
    sys.exit(1)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description='Creates, trains and saves the given iteration of the AI model'
  )
  parser.add_argument(
    '--model_type', '-t', type=str,
    default='recurrentLSTM',
    help='the model iteration to use [default is recurrentLSTM]'
  )
  parser.add_argument(
    '--model_file', '-m', type=str,
    default=os.path.join(os.path.dirname(__file__), '../models/model.pkl'),
    help='the path of the file where the trained model will be saved [default is models/model.pkl]'
  )
  parser.add_argument(
    '--input_file', '-i', type=str,
    default=os.path.join(os.path.dirname(__file__), '../data/processed_data.csv'),
    help='the path of the file where training data is stored [default is data/processed_data.csv]'
  )
  args = parser.parse_args()
  main(args)
