import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

class DatasetWrapper:
  def __init__(self, df_csv, batch_size, window_size, countries_in_use, country_hyperparams, phase="inference"):
    self.df = self._load_df(filePath=df_csv)
    self.df_length           = len(self.df)
    self.batch_size          = batch_size
    self.window_size         = window_size
    self.countries_in_use    = countries_in_use
    self.country_hyperparams = country_hyperparams
    self.phase               = phase

    # Adapt hyperparameters to the input of the model
    self.df = self._transform_to_circular_timevalues(self.df)
    self.df = self._prepend_empty_rows(self.df, self.window_size-1)

    # Split the dataframe into one dataframe per country
    self.country_dfs = self._split_country_dfs(self.df, self.countries_in_use)
    self.country_dfs = self._filter_unused_hyperparams(self.country_dfs, self.country_hyperparams)
  
  def get_train_test_split_iterables(self, test_size=0.2):
    training_size = int(self.df_length*(1-test_size))
    return (
      self._get_iterable(0,             training_size ),
      self._get_iterable(training_size, self.df_length)
    )

  def get_whole_dataset_iterable(self):
    return self._get_iterable(0, self.df_length)

  def _get_iterable(self, it_start_index, it_end_index):
    for batch_start_index in range(it_start_index+self.window_size, it_end_index+self.window_size-1, self.batch_size):
      batch_end_index = batch_start_index + self.batch_size
      if batch_end_index > it_end_index+self.window_size-1:
        batch_end_index = it_end_index+self.window_size-1
      if self.phase == "inference":
        yield np.asarray(self._process_batch(batch_start_index, batch_end_index))
      elif self.phase == "training":
        yield self._process_batch(batch_start_index, batch_end_index)
  
  def _process_batch(self, start_index, end_index):
    batch = np.empty(shape=(end_index-start_index, len(self.countries_in_use), self.window_size, len(self.country_hyperparams)))
    if self.phase == "training":
      batch_labels = np.empty(shape=(end_index-start_index))
    for batch_index, sample_index in enumerate(range(start_index, end_index)):
      for country in self.countries_in_use:
        country_window = self.country_dfs[country].iloc[sample_index-self.window_size+1 : sample_index+1]
        batch[batch_index, self.countries_in_use.index(country)] = country_window.values.reshape(self.window_size, -1)
      if self.phase == "training":
        batch_labels[batch_index] = self.df.iloc[sample_index]["label"]
    if self.phase == "training":
      return batch, batch_labels
    else:
      return batch

  @staticmethod
  def _load_df(filePath):
    df = pd.read_csv(filePath, index_col=0)
    df['Time'] = pd.to_datetime(df['Time'])
    return df

  @staticmethod
  def _transform_to_circular_timevalues(df):
    df['Time_hour_x'],  df['Time_hour_y']  = zip(*df.apply(lambda row: DatasetWrapper._calculate_circular_coordinates(row['Time'], 'hour' ), axis=1))
    df['Time_week_x'],  df['Time_week_y']  = zip(*df.apply(lambda row: DatasetWrapper._calculate_circular_coordinates(row['Time'], 'week' ), axis=1))
    df['Time_month_x'], df['Time_month_y'] = zip(*df.apply(lambda row: DatasetWrapper._calculate_circular_coordinates(row['Time'], 'month'), axis=1))
    return df.drop(columns=['Time'])

  @staticmethod
  def _calculate_circular_coordinates(timestamp, stage):
    if stage == 'hour':
      return DatasetWrapper._circular_coordinates(24)[timestamp.hour]
    elif stage == 'week':
      return DatasetWrapper._circular_coordinates(7)[timestamp.weekday()]
    elif stage == 'month':
      return DatasetWrapper._circular_coordinates(12)[timestamp.month-1]
    else:
      raise ValueError(f"Invalid stage: {stage}")
  
  @staticmethod
  def _circular_coordinates(num_points): # TODO not generate the entire array, as it is not needed
    radians = np.linspace(0, 2*np.pi, num_points, endpoint=False)
    return np.column_stack((np.cos(radians), np.sin(radians)))
  
  @staticmethod
  def _prepend_empty_rows(df, num_rows):
    # Add num_rows to the beggining of the dataframe and recalculate the index
    return pd.concat([pd.DataFrame(np.zeros((num_rows, df.shape[1])), columns=df.columns), df], ignore_index=True)

  @staticmethod
  def _split_country_dfs(df, countries):
    return {
      country_code: df[[col for col in df.columns if col.startswith(('Time', 'label', country_code))]]
      for country_code in countries
    }
  
  @staticmethod
  def _filter_unused_hyperparams(country_dfs, hyperparams):
    # check if col ends with any of the hyperparams
    return {
      country_code: df[[col for col in df.columns if any(col.endswith(hyperparam) for hyperparam in hyperparams)]]
      for country_code, df in country_dfs.items()
    }
