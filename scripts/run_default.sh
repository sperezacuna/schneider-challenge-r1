#!/bin/bash

# Does not include model training

# Monitors performance at each stage; particularly:
#   How many data points have we ingested?
#   Do we lose any data during data processing?
#   Which data have we lost?
#   Why did we lose it?
#   Any other more specific measures

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create the virtual environment
python -m venv $script_dir/../env
# Check if creation was successful
if [ "$?" -ne "0" ]; then
  echo "Error creating the virtual environment."
  exit 1
fi
# Activate the virtual environment
if [ -f "$script_dir/../env/bin/activate" ]; then
  source "$script_dir/../env//bin/activate"
  echo "Virtual environment activated. You can deactivate it later with 'deactivate'."
elif [ -f "$script_dir/../env/Scripts/activate" ]; then
  source "$script_dir/../env/Scripts/activate"
  echo "Virtual environment activated. You can deactivate it later with 'deactivate'."
else
  echo "Failed to activate the virtual environment. Check the environment structure."
  exit 1 
fi

# Install the requirements
pip install -r $script_dir/../requirements.txt
echo "Requirements installed."

# Run the data ingestion script
python $script_dir/../src/data_ingestion.py --output_file "$script_dir/../data/raw_data.csv"
echo "Finished data ingestion."

# Run the data processing script
python $script_dir/../src/data_processing.py --input_file "$script_dir/../data/raw_data.csv" --output_file "$script_dir/../data/processed_data.csv"
echo "Finished data processing."

# Run the model prediction script
python $script_dir/../src/model_prediction.py --model_type "recurrentLSTM" --model_file "$script_dir/../models/model.pkl" --input_file "$script_dir/../data/test.csv" --output_file "$script_dir/../predictions/predictions.csv"
echo "Finished inference."