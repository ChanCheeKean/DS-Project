# Layout for forecasting page
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from app import app
from utils.graph_helpers import get_ts_plot, get_box_plot, get_ts_plot_outlier
from utils.data_importer import transformers, get_reading, get_channel, get_phase
from utils.statictis_helpers import get_sh_esd,  get_excur_percent
from datetime import datetime, timedelta

# initial data
@app.callback(
        Output('analytic_intermediate', 'children'), 
        [Input('analytic_button','n_clicks')], 
        [State('analytic_station', 'value'), 
         State('analytic_date', 'start_date'), 
         State('analytic_date', 'end_date'),
         State('analytic_res_value','value'),
         State('analytic_res_unit','value')])
def select_data(n_clicks, station, start, end, res_value, res_unit):
    
     # get station data and resampling 
    df = get_reading(station)
    df = df.resample(f'{res_value}{res_unit}').mean()
    df = df[(df.index >= start) & (df.index < end)]
    
    # apparent power
    for i in range(3):
                df['S'+str(i+1)] = np.sqrt(df['P'+str(i+1)]**2 + df['Q'+str(i+1)]**2)   
    
    return df.to_json()

# anamolies plot
@app.callback (Output('anomalies_plot', 'figure'),  
               [Input('analytic_intermediate', 'children'), Input('ana_var', 'value')])
def update_dev_graph (json_data, var):
    try:
        # call data
        df = pd.read_json(json_data)
        df = df[[col for col in df.columns if var in col]]
        
        # comptue MAD
        df_mad = df.mad(axis = 1)
        alpha = 1 - 0.1
        idx = get_sh_esd(df_mad, alpha = alpha)
        
        # get outlier
        if idx != None:
            df_out = df_mad[idx]
            fig = get_ts_plot_outlier(df_mad, df_out, yaxis_label = 'MAD')
        else:
            fig = get_ts_plot(df_mad, title = 'Anamoly Detection of Unbalances in {}'.format(var), yaxis_label = 'MAD', )
        return fig
    except:
        return []
    
# voltage excursion
@app.callback (Output('vex_plot', 'figure'),  
               [Input('analytic_intermediate', 'children'), Input('vex_ma_range', 'value')])
def update_volt_excurs_graph (json_data, ma_win):
    try:        
        # call data
        df_trans = pd.read_json(json_data).copy()
        
        # compute excursion percentage
        df_1 = get_excur_percent(df_trans, ma_win, channel = 'V')
        
        # plotting
        fig = get_ts_plot(df_1, yaxis_label = '% Change (from MA)')
        return fig
    except:
        return []
 
# power factor
@app.callback (Output('pf_plot', 'figure'),
               [Input('analytic_intermediate', 'children')])
def update_pf_graph (json_data):
    try:        
        df = pd.read_json(json_data).copy()
        
        # power factor
        df_P = df[[col for col in df.columns if 'P' in col]].copy()
        df_S = df[[col for col in df.columns if 'S' in col]].copy()
        
        df_pf = df_P.values/df_S.values
        df_pf = pd.DataFrame(df_pf, index = df_P.index, columns = ['Pf1','Pf2','Pf3'])
        fig_pf = get_ts_plot(df_pf, yaxis_label = ' ', hover_mode = 'x')
        return fig_pf
    except:
        return []
    
# corr
@app.callback (Output('roll_corr_plot', 'figure'),
               [Input('analytic_intermediate', 'children'), Input('rolling_step', 'value')])
def update_corr_graph (json_data, step):
    try:        
        df = pd.read_json(json_data).copy()        
         # current vs power corr
        for i in range(1,4):
            df[f'Corr{i}'] = df[f'S{i}'].rolling(step).corr(df[f'I{i}'].rolling(step))
        df_corr = df[[col for col in df.columns if 'Corr' in col]].copy()
        fig_corr = get_ts_plot(df_corr, yaxis_label = ' ', hover_mode = 'x')
        return fig_corr
    except:
        return []
