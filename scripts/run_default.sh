#!/bin/bash

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
echo "Installing requirements..."
pip install -r $script_dir/../requirements.txt
echo "Requirements installed."

# Run the data ingestion script
echo "Starting data ingestion..."
python $script_dir/../src/data_ingestion.py --start_time 2022-01-01 --end_time 2023-01-01 --output_file "$script_dir/../data/raw_data.csv"
echo "Finished data ingestion."

# Run the data processing script
echo "Starting data processing..."
python $script_dir/../src/data_processing.py --input_file "$script_dir/../data/raw_data.csv" --output_file "$script_dir/../data/processed_data.csv"
echo "Finished data processing."

# Run the model prediction script
echo "Starting prediction..."
python $script_dir/../src/model_prediction.py --model_type "recurrentLSTM" --model_file "$script_dir/../models/model.pkl" --input_file "$script_dir/../data/test.csv" --output_file "$script_dir/../predictions/predictions.json"
echo "Finished inference."

echo "Pipeline completed."