# jittering
import pandas as pd
import numpy as np
import math

# read  full data
df_loc = pd.read_csv('./ori_loc.csv', index_col = None)
df_loc ['Jitter_Lon'] = np.nan
df_loc ['Jitter_Lat'] = np.nan

# Jittering loop
for loc in df_loc['location'].unique():
    df_temp = df_loc[df_loc['location'] == loc] 
    a = df_temp['lon'].mean()
    b = df_temp['lat'].mean()    
    r = 0.001
    no_points = len(df_temp['transformer'].unique())    
    angle_list = np.linspace(0, 360, no_points+1)
    
    for i ,trans_items in enumerate(df_temp['transformer'].unique()):
        x = r * math.sin(math.radians(angle_list[i])) + a
        y = r * math.cos(math.radians(angle_list[i])) + b
        df_loc['Jitter_Lon'][df_loc['transformer']==trans_items] = x
        df_loc['Jitter_Lat'][df_loc['transformer']==trans_items] = y 

df_loc.drop(columns = ['lat','lon'], inplace = True)
df_loc.columns = ['transformer', 'location', 'Lon', 'Lat']
df_loc.to_csv('../data/locations/transformer_loc.csv')
