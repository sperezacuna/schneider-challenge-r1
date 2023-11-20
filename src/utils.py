import os
import configparser

from datetime import datetime

def load_config():
  config = configparser.ConfigParser()
  config.read(os.path.join(os.path.dirname(__file__), 'config/config.ini'))
  return config

def inspect_dataframe(dataframe, filename):
  save_file = os.path.join(os.path.dirname(__file__), '../doc/df_sizes.txt')
  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  df = dataframe
  num_rows, num_columns = df.shape

  with open(save_file, 'a') as f:
    f.write(f"File analized: {os.path.basename(filename)}\n")
    f.write(f"Timestamp: {timestamp}\n")
    f.write(f"Number of Rows: {num_rows}\n")
    f.write(f"Number of Columns: {num_columns}\n")
    f.write("----------------------------\n\n\n")
  
  print(f"Row and cols data about {filename} has been added to: {save_file}\n")