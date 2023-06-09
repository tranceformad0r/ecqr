import tensorflow as tf
import os
import numpy as np
import pandas as pd
from datetime import timedelta

def get_met_data():
    """
    Taken from Tensorflow tutorial on time series forecasting:
    https://www.tensorflow.org/tutorials/structured_data/time_series
    """
    
    zip_path = tf.keras.utils.get_file(
        origin='https://storage.googleapis.com/tensorflow/tf-keras-datasets/jena_climate_2009_2016.csv.zip',
        fname='jena_climate_2009_2016.csv.zip',
        extract=True)
    csv_path, _ = os.path.splitext(zip_path)
    df = pd.read_csv(csv_path)
    # Slice [start:stop:step], starting from index 5 take every 6th record.
    df = df[5::6]
    date_time = pd.to_datetime(df.pop('Date Time'), format='%d.%m.%Y %H:%M:%S')
    
    # Convert wind from direction/velocity to (x,y) components
    wv = df.pop('wv (m/s)')
    max_wv = df.pop('max. wv (m/s)')
    # Convert to radians.
    wd_rad = df.pop('wd (deg)')*np.pi / 180
    # Calculate the wind x and y components.
    df['Wx'] = wv*np.cos(wd_rad)
    df['Wy'] = wv*np.sin(wd_rad)
    # Calculate the max wind x and y components.
    df['max Wx'] = max_wv*np.cos(wd_rad)
    df['max Wy'] = max_wv*np.sin(wd_rad)
    
    # Represent time with periodic signals
    timestamp_s = date_time.map(pd.Timestamp.timestamp)
    day = 24*60*60
    year = (365.2425)*day
    df['Day sin'] = np.sin(timestamp_s * (2 * np.pi / day))
    df['Day cos'] = np.cos(timestamp_s * (2 * np.pi / day))
    df['Year sin'] = np.sin(timestamp_s * (2 * np.pi / year))
    df['Year cos'] = np.cos(timestamp_s * (2 * np.pi / year))

    return df


def get_solar_data():
    url = 'https://raw.githubusercontent.com/Duvey314/austin-green-energy-predictor/master/Resources/Output/Webberville_Solar_2017-2020_MWH.csv'
    df = pd.read_csv(url)
    df = df.drop(columns=('Weather_Description'))
    df = df.drop(columns=('Year'))
    df = df.drop(columns=('Month'))
    df = df.drop(columns=('Day'))
    df = df.drop(columns=('Hour'))
    df = df.drop(columns=('Date_Time'))
    df = df.drop(columns=('Temperature_F'))
    df = df.drop(columns=('Humidity_percent'))
    df = df.drop(columns=('Sunhour'))
    df = df.drop(columns=('CloudCover_percent'))
    df = df.drop(columns=('uvIndex'))
       
    # create date+hour index 
    date_list = pd.date_range(start='01/01/2017', end='31/07/2020')
    date_list = pd.to_datetime(date_list)
    hour_list = []
    for nDate in date_list:
        for nHour in range(24):
            tmp_timestamp = nDate+timedelta(hours=nHour)
            hour_list.append(tmp_timestamp)
    date_list = pd.to_datetime(hour_list) 
    df['hour_list'] = date_list[:-1]
    df = df.set_index('hour_list')
    
    # train, val, test datasets
    df_train = df[0:365*24]
    df_val = df[365*24:365*24*2]
    df_test = df[365*24*2:365*24*3]
    
    print(df_train.shape[0] + df_test.shape[0] + df_val.shape[0])
    
    return df_train, df_val, df_test

def get_gas_data(split_perc, usage_perc=1,version='new',test_days=None):
    if version == "new":
        csv_path = './TTF_FM_new.csv'
    else:
        csv_path = './TTF_FM_old.csv'
    data = pd.read_csv(csv_path, sep=";")
    df = pd.DataFrame(data, columns=['Price'])
    index = range(len(df))
    df['hour_list'] = index
    df.set_index(df.pop('hour_list'))
    if test_days is not None:
        n = len(df)-test_days
        assert(split_perc[0] + split_perc[1] == 1)
        df_test = df[len(df) - test_days:]
    else:
        n = int(len(df)*usage_perc)
        df_test = df[int((split_perc[0] + split_perc[1])*n):n]
    df_train = df[0:int(split_perc[0]*n)]
    df_val = df[int(split_perc[0]*n):int((split_perc[0] + split_perc[1])*n)]
    
    
    return df_train, df_val, df_test