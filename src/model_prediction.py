import os
import sys
import json
import argparse

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from dataset_helpers import DatasetWrapper

def main(args):
  model = load_model(args.model_type, args.model_file)
  data = DatasetWrapper(
    df_csv=os.path.abspath(args.input_file),
    batch_size=model.batch_size,
    window_size=model.window_size,
    countries_in_use=model.countries_in_use,
    country_hyperparams=model.country_hyperparams,
    phase="inference"
  )
  save_predictions(model.predict(data), args.output_file)

def load_model(model_type, model_path):
  if model_type == "recurrentLSTM":
    from models import RecurrentLSTMModel
    return RecurrentLSTMModel(os.path.abspath(model_path))
  else:
    print("[!] Invalid model type")
    sys.exit(1)
    
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
    description='Performs predictions using the given iteration of the AI model'
  )
  parser.add_argument( 
    '--model_type', '-t', type=str,
    default='recurrentLSTM',
    help='the model type to use [default is recurrentLSTM]'
  )
  parser.add_argument(
    '--model_file', '-m', type=str,
    default=os.path.join(os.path.dirname(__file__), '../models/model.pkl'),
    help='the path of the file where the trained model is stored [default is models/model.pkl]'
  )
  parser.add_argument(
    '--input_file', '-i', type=str,
    default=os.path.join(os.path.dirname(__file__), '../data/test.csv'),
    help='the path of the file where the inference data is be stored [default is data/test.csv]'
  )
  parser.add_argument(
    '--output_file', '-o', type=str,
    default=os.path.join(os.path.dirname(__file__), f'../predictions/predictions.json'),
    help='the path of the file where the predictions made by the model will be stored [default is predictions/predictions.json]. The folder must exist'
  )
  args = parser.parse_args()
  main(args)