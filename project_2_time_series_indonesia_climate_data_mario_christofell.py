# -*- coding: utf-8 -*-
"""Project 2 Time Series Indonesia Climate Data Mario Christofell.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MNXRcAmh_lVtvtZweaER8UwnySmtaPec

# Mario Christofell L.Tobing

Project 2 Dicoding Modul Belajar Pengembangan Machine Learning 

*   Machine Learning Model Time Series Indonesia Climate Data 
*   Dataset download from Kaggle : Climate Data Daily IDN (https://www.kaggle.com/datasets/greegtitan/indonesia-climate?select=climate_data.csv)

# Import Library
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

from sklearn.model_selection import train_test_split
from keras.layers import LSTM,Dense,Bidirectional
from keras.callbacks import EarlyStopping

"""# Read Dataset into Dataframe"""

df = pd.read_csv('/content/drive/MyDrive/climate_data.csv') # Link download dataset Kaggle : Climate Data Daily IDN (https://www.kaggle.com/datasets/greegtitan/indonesia-climate?select=climate_data.csv)
df.head()

df.drop(['Tn','Tx','RH_avg', 'RR','ss','ff_x','ddd_x','ff_avg','ddd_car','station_id'], axis=1, inplace=True) # drop column yang tidak dipakai
df

df['date'] = pd.to_datetime(df['date'])  
get_data = (df['date'] > '01-01-2020') & (df['date'] <= '31-12-2020') # mengambil sampel data dari tahun 2020
df.loc[get_data]

df = df.loc[get_data]
df

df.reset_index(drop=True)

df.info() # info dataset

df.isnull().sum() # mengecek adakah nilai yang hilang pada dataset

df.dropna(subset=['Tavg'],inplace=True) # mendrop baris pada kolom Tavg yg tidak memiliki nilai atau null/Nan
df.isnull().sum()

"""Membuat plot dataset Indonesia Climate 2020 """

dates = df['date'].values
tempavg  = df['Tavg'].values


plt.figure(figsize=(18,8))
plt.plot(dates, tempavg)
plt.title('Indonesia Climate Data 2020',fontsize=20);

"""# Split Dataset"""

x_train, x_test, y_train, y_test = train_test_split(tempavg, dates, test_size = 0.2, shuffle = False)  # pembagian dataset untuk data test/validation sebesar 20% dari total keseluruhan data

"""# Model

Mengubah format data untuk dapat diterima oleh model
"""

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    return ds.batch(batch_size).prefetch(1)

"""Pemodelan Sequential dengan LSTM"""

train_set = windowed_dataset(x_train, window_size=60, batch_size=100, shuffle_buffer=1000)
test_set = windowed_dataset(x_test, window_size=60, batch_size=100, shuffle_buffer=1000)
model = tf.keras.models.Sequential([
  tf.keras.layers.Bidirectional(LSTM(60, return_sequences=True)),
  tf.keras.layers.Bidirectional(LSTM(60)),
  tf.keras.layers.Dense(30, activation="relu"),
  tf.keras.layers.Dense(10, activation="relu"),
  tf.keras.layers.Dense(1),
])

mx = df['Tavg'].max()
print('Max value : ' )
print(mx)

mn = df['Tavg'].min()
print('Min value : ' )
print(mn)

m = (33.6 - 16.1) * (10 / 100) # MAE < 10%
print(m)

"""Membuat fungsi callback"""

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('mae')< m and logs.get('val_mae')< m): # Pelatihan berhenti ketika memenuhi nilai MAE < 10% skala data
      print("\nThe MAE has reached < 10% from data scale")
      self.model.stop_training = True
callbacks = myCallback()

"""Optimizer dan Penggunaan Learning Rate"""

optimizer = tf.keras.optimizers.SGD(learning_rate=1.0000e-04, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])
history = model.fit(train_set, epochs=100, batch_size=128, validation_data=test_set, callbacks=[callbacks])

"""Visualization Plot MAE and Loss """

plt.plot(history.history['mae']) # plot MAE
plt.plot(history.history['val_mae'])
plt.title('Plot MAE')
plt.ylabel('mae')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper right')
plt.show()

plt.plot(history.history['loss']) # plot loss
plt.plot(history.history['val_loss'])
plt.title('Plot Loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper right')
plt.show()