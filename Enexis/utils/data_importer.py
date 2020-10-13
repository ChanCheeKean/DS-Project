import pandas as pd
import pytz
from os import listdir
from os.path import isfile, join
import numpy as np

# set timezone
timezone = pytz.timezone('Europe/Berlin')

# list of station, should have done it in proper table format
transformers = ['VRY.CHOPS-1', 'VRY.LUITS-1', 'VRY.RAHUS-1', '019.671-1', 'ESD.000381-1']

def get_reading(station_name = 'VRY.CHOPS-1'):
    '''
	Input: any of ['VRY.CHOPS-1', 'VRY.LUITS-1', 'VRY.RAHUS-1', '019.671-1', 'ESD.000381-1']
	Output: DataFrame Object. Inclusive of Power, Voltage, Current, etc.	
	'''
    df = pd.read_csv('./data/{0}.csv'.format(station_name), index_col = 0)
    df.index = pd.to_datetime(df.index, errors='coerce')
    df = df.astype('float64')
    df = df.interpolate('linear')
    return df

def get_channel(df, channel):
    '''
	Input: Targeted DataFrame and channel name, e.g. 'Voltage'
	Output: DataFrame Object. 
	'''
    # channel can be apow, volt, curr etc
    colname = [col for col in df.columns if channel in col[:-1]]
    df_channel = df[colname]
    return df_channel

def get_phase (df, phase):
    '''
	Input: Targeted DataFrame and Phase. 1,2 or 3
	Output: DataFrame Object. 
	'''
    colname = [col for col in df.columns if phase == col[-1]]
    df_p = df[colname]
    return df_p
