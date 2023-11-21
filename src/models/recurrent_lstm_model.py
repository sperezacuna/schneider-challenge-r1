import os
import keras
import pickle
import numpy as np

from utils import load_config
from keras.models import Model
from keras.losses import CategoricalCrossentropy
from keras.layers import Input, Masking, LSTM, Dense, Dropout, BatchNormalization, Concatenate
from keras.optimizers import Adam
from keras.callbacks import Callback
from sklearn.metrics import f1_score

from constants import countries

class RecurrentLSTMModel():
  def __init__(self, filePath=None):
    config = load_config()
    self.save_graphs         = config.getboolean('Common', 'SaveGraphs')
    self.batch_size          = config.getint('RecurrentLSTMModel', 'BatchSize')
    self.window_size         = config.getint('RecurrentLSTMModel', 'WindowSize')
    self.num_epochs          = config.getint('RecurrentLSTMModel', 'NumEpochs')
    self.lstm_units          = config.getint('RecurrentLSTMModel', 'LSTMUnits')
    self.validation_split    = config.getfloat('RecurrentLSTMModel', 'ValidationSplit')
    self.learning_rate       = config.getfloat('RecurrentLSTMModel', 'LearningRate')
    self.countries_in_use    = config.get('RecurrentLSTMModel', 'CountriesInUse').split(',')
    self.country_hyperparams = config.get('RecurrentLSTMModel', 'CountryHyperparams').split(',')
    if filePath:
      self._load_model(filePath)
    else:
      self._create_model()
  
  def train(self, dataset):
    training, validation = dataset.get_train_test_split_iterables(self.validation_split, repeat=True)
    self.model.fit(training,
      epochs=self.num_epochs,
      steps_per_epoch=int(dataset.df_length*(1-self.validation_split)//self.batch_size),
      validation_data=validation,
      validation_steps=int(dataset.df_length*self.validation_split//self.batch_size),
      verbose=1
    )

  def predict(self, dataset):
    to_predict = dataset.get_whole_dataset_iterable(repeat=False)
    prediction = self.model.predict(to_predict, verbose=1)
    all_preds = [ int(np.argmax(vector)) for vector in prediction ]
    all_preds = all_preds[:dataset.df_length]
    return all_preds

  def save(self, filePath):
    pickle.dump(self.model, open(filePath, 'wb'))

  def _load_model(self, filePath):
    self.model = pickle.load(open(filePath, 'rb'))
  
  def _create_model(self):
    input_shape = (len(self.countries_in_use), self.window_size, len(self.country_hyperparams)-1)
    input_layer = Input(shape=input_shape, batch_size=self.batch_size)

    per_country_nets = []
    for i in range(len(self.countries_in_use)):
      country_net = self._create_country_network(input_layer[:, i, :, :], self.lstm_units)
      per_country_nets.append(country_net)
    
    combined_model = Concatenate()(per_country_nets)

    # Extra layers processed after combination
    fused_dense1 = Dense(240, activation="relu")(combined_model)
    fused_bn1 = BatchNormalization(axis=-1)(fused_dense1)
    fused_dense2 = Dense(120, activation="relu")(fused_bn1)
    fused_bn2 = BatchNormalization(axis=-1)(fused_dense2)
    fused_dense3 = Dense(30, activation="relu")(fused_bn2)
    fused_bn3 = BatchNormalization(axis=-1)(fused_dense3)
    fused_drop1 = Dropout(0.2)(fused_bn3)
    fused_bn4 = BatchNormalization(axis=-1)(fused_drop1)
    fused_dense4 = Dense(len(countries), activation="softmax")(fused_bn4)

    #Construct the final model
    self.model = keras.models.Model(inputs=input_layer, outputs=fused_dense4)
    
    if self.save_graphs: 
      keras.utils.plot_model(self.model, show_shapes=True, to_file=os.path.join(os.path.dirname(__file__), '../../doc/lstm_structure.png'))
   
    #Compile
    self.model.compile(
      loss=CategoricalCrossentropy(), 
      optimizer=Adam(learning_rate=self.learning_rate),
      metrics=['accuracy']
    )
  
  @staticmethod
  def _create_country_network(input_layer_segment, lstm_units):
    country_mask = Masking(mask_value=0.0)(input_layer_segment)
    country_lstm = LSTM(units=lstm_units, stateful=True)(country_mask)
    country_bn1 = BatchNormalization(axis=-1)(country_lstm)
    country_dense1 = Dense(600, activation = 'relu')(country_bn1)
    country_bn2 = BatchNormalization(axis=-1)(country_dense1)
    country_dense2 = Dense(300, activation = 'relu')(country_bn2)
    country_bn3 = BatchNormalization(axis=-1)(country_dense2)
    country_dense3 = Dense(120, activation = 'relu')(country_bn3)
    country_bn4 = BatchNormalization(axis=-1)(country_dense3)
    country_dense4 = Dense(9, activation= 'linear')(country_bn4)
    country_bn5 = BatchNormalization(axis=-1)(country_dense4)
    return country_bn5
