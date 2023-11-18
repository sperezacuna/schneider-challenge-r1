import os
import configparser

def load_config():
  config = configparser.ConfigParser()
  config.read(os.path.join(os.path.dirname(__file__), 'config/config.ini'))
  return config
