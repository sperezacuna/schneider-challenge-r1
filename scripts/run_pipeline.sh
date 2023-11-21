#!/bin/bash

# You can run this script from the command line using:
# ./run_pipeline.sh <start_date> <end_date> <raw_data_file> <processed_data_file> <model_file> <test_data_file> <predictions_file>
# For example:
# ./run_pipeline.sh 2020-01-01 2020-01-31 data/raw_data.csv data/processed_data.csv models/model.pkl data/test_data.csv predictions/predictions.json

# Get command line arguments
start_date="$1"
end_date="$2"
raw_data_file="$3"
processed_data_file="$4"
model_file="$5"
test_data_file="$6"
predictions_file="$7"

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
python $script_dir/../src/data_ingestion.py --start-time $start_date --end-time $end_date --output_file $raw_data_file
echo "Finished data ingestion."

# Run the data processing script
echo "Starting data processing..."
python $script_dir/../src/data_processing.py --input_file $raw_data_file --output_file $processed_data_file
echo "Finished data processing."

# Run the model prediction script
echo "Starting prediction..."
python $script_dir/../src/model_prediction.py --model_type "recurrentLSTM" --model_file $model_file --input_file $test_data_file --output_file $predictions_file
echo "Finished inference."
echo "Pipeline completed."
