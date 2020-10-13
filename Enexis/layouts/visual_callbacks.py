# Layout for forecasting page
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from app import app
from utils.data_importer import transformers, get_reading, get_channel, get_phase
from utils.rest_helper import read_files
from utils.graph_helpers import get_ts_plot, get_heatmap, get_corr_heatmap
from datetime import datetime, timedelta
import calendar

# initial data
@app.callback(
        Output('visual_intermediate', 'children'), 
        [Input('vs_data_button','n_clicks')], 
        [State('vs_station_picker', 'value'), 
         State('vs_date-picker', 'start_date'), 
         State('vs_date-picker', 'end_date'),
         State('vs_res_value','value'),
         State('vs_res_unit','value')])
def select_data(n_clicks, station, start, end, res_value, res_unit):
    
    # get station data and resampling 
    df = get_reading(station)
    df = df.resample(f'{res_value}{res_unit}').mean()
    df = df[(df.index >= start) & (df.index < end)]
    return df.to_json()

# time series
@app.callback (
        Output('vs_ts', 'figure'),  
        [Input('visual_intermediate', 'children')], 
        [State('vs_var', 'value')])

def update_timeSeries_graph (json_data, var):
    try:
        # call dat
        df = pd.read_json(json_data)
        colname = [col for col in df.columns if var in col]        
        df = df[colname]
        
        fig = get_ts_plot(df, yaxis_label = '')
        return fig
    except:
        return []

## average graph
@app.callback (
        Output('vs_avg_plot', 'figure'),  
        [Input('vs_avg_radio', 'value'), Input('visual_intermediate', 'children')],
        [State('vs_var', 'value')])
def update_average_graph (datetype, json_data, var):
        df = pd.read_json(json_data)
        df = df [ [col for col in df.columns if var in col]]
        
        if datetype == 'Month':
            df = df.groupby(df.index.month).mean()
            df.index = df.index.map(lambda x: calendar.month_name[x])
        elif datetype == 'Hour':
            df = df.groupby(df.index.hour).mean()
        
        elif datetype == 'Dai':
            df = df.groupby(df.index.day).mean()
        else:
            df = df.groupby(df.index.dayofweek).mean()
            df.index = df.index.map(lambda x: calendar.day_name[x])
            
        fig = get_ts_plot(df, yaxis_label = '', convert_x = False, xtick = 1)
        return fig

# heatmap
# grouping by heatmap
@app.callback (
        Output('vs_hm', 'figure'),  
        [Input('vs_hm_radio', 'value'), Input('vs_hm_picker', 'value'), Input('visual_intermediate', 'children')],
        [State('vs_var', 'value')]
        )
def update_heatmap (graph_type, phase, json_data, var):
    
        df = pd.read_json(json_data)  
        # filter by var
        df = df[[col for col in df.columns if var in col]]
        # filter by phase
        df =  df[[col for col in df.columns if col[-1] == str(phase)]]
                
        if graph_type == 'MvD':
            x_value = df.index.day
            y_value = df.index.month
            x_title = 'Days'
            y_title = 'Months'

        elif graph_type == 'DvH' :
            x_value = df.index.hour
            y_value = df.index.day
            x_title = 'Hours'
            y_title = 'Days'

        else:
            x_value = df.index.hour
            y_value = df.index.month
            x_title = 'Hours'
            y_title = 'Months'

        fig = get_heatmap(df, x_value, y_value,  df.columns.values[0], x_title, y_title)
        return fig
    
# correlation heatmap
@app.callback (Output('corr_hm', 'figure'), 
               [Input('visual_intermediate', 'children'), Input('vs_corr_phase', 'value'),  Input('vs_corr_var', 'value')])
def update_corr_heatmap (json_data, phase, var):
    try:
        df = pd.read_json(json_data)
        if var != 'All':
            df = df[[col for col in df.columns if var in col]]
        else: 
            pass
        if phase != 'All':
             # filter by phase
             df =  df[[col for col in df.columns if col[-1] == str(phase)]]
        else: 
            pass
        
        fig = get_corr_heatmap(df, title = 'Linear Correlation Heatmap')
        return fig
    except:
        return []    
    
# normalized plot
@app.callback (
        Output('norm_plot', 'figure'),  
        [
         Input('visual_intermediate', 'children'), 
         Input('vs_norm_phase', 'value'),  
         Input('vs_norm_var', 'value')])
def update_normalized_graph (json_data, phase, var):
    try:
        df = pd.read_json(json_data)
        if var != 'All':
            df = df[[col for col in df.columns if var in col]]
        else: 
            pass
        if phase != 'All':
             # filter by phase
             df =  df[[col for col in df.columns if col[-1] == str(phase)]]
        else: 
            pass
        
        df_zs = (df-df.mean())/df.std()
        fig = get_ts_plot(df_zs, yaxis_label = 'z-score')
        return fig
    except:
        return []


#for a in asset_list:
#    try:
#        read_files(a)
#    except:
#        print(a)
    