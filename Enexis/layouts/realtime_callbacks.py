# Layout for forecasting page
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from app import app
from utils.graph_helpers import get_ts_plot
from datetime import datetime, timedelta
from utils.forecast_helpers import prepare_fc_data, train_fc_model, get_pv_peak
import json
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from utils.data_importer import get_reading, get_channel, get_phase
import pickle

##################
# import data
##################
with open('./forecast_models/scaler_new.sav', 'rb') as sm:
    sc = pickle.load(sm)  
df_temp = get_reading(station_name = 'VRY.CHOPS-1').abs()
df_temp['Total Power'] = get_channel(df_temp, 'P').sum(axis=1)
dt = col_list = step_count = n = reg = delta = []
df_mock = df_live = df_predict = []
df_load = df_live_load = []
col_list = list(set([col[:-1] for col in df_temp.columns]))


##################
# callbacks
##################
# on/off button to disable random data
@app.callback(Output('real_interval_comp', 'disabled'), [Input('on_button', 'on')])
def start_app(on):
    return not on    

# Change global variable
@app.callback(Output('real_int_data','children'), [Input('show_button','n_clicks')],
              [State('real_step', 'value')])
def change_global (n_clicks, fc_step):
    res_unit = 'H'
    res_value = 1
    
    global df_temp, df_mock, df_live, df_predict, dt, step_count, n, reg, delta, df_load, df_live_load
    delta = timedelta(hours = res_value)
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    dt = []
    dt.append(now)
    step_count = int(fc_step)
    # phase for training, phase 2 as real data
    df_mock = prepare_fc_data(df_temp, time_res = '{}{}'.format(res_value,res_unit), phase = None, y_var = 'Total Power')    
    df_load = pd.read_csv('./data/additional/pv_load.csv', index_col = 0)
    df_load.index = pd.to_datetime(df_load.index, errors='coerce')    
    df_load = prepare_fc_data(df_load, time_res = '{}{}'.format(res_value,res_unit), phase = None, y_var = 'PV Production')
    df_load = df_load[df_load.index.month>3]
    df_mock = df_mock[df_mock.index.month>3]
    # empty dataframe
    df_live = pd.DataFrame(columns = df_mock.columns)
    df_predict = pd.DataFrame(columns = ['Predicted'])
    df_live_load = pd.DataFrame(columns = df_load.columns)
    # train model 
    df_act_pred, metrics, reg = train_fc_model (df_mock, y_var = 'Total Power', model='rf', step = step_count)
    # current date - 1 year
    r_now = now.replace(year = 2018, month = 5)
    d1 = pd.DataFrame(df_mock.index, columns = ['date'])
    n = d1[d1.date == r_now.strftime('%Y-%m-%d %H:%M:%S')].index.values[0]
    return df_act_pred.to_json()

# generate random number
@app.callback(Output('real_intermediate', 'children'), 
              [Input('real_interval_comp', 'n_intervals'), Input('real_int_data','children')])
def generate_random_data (n_clicks, json_data):
        global n, df_mock, df_live, df_predict, dt, step_count, delta, sc, reg, df_load, df_live_load
    
        df_now = df_mock.iloc[n:n+1,:]
        # predict next value
        df_now = sc.transform(df_now) 
        pred_y = reg.predict(df_now)
        # generate live data
        df_live.loc[dt[-1].strftime("%Y-%m-%d %H:%M")] = df_mock.iloc[n:n+1,:].squeeze()
        df_live_load.loc[dt[-1].strftime("%Y-%m-%d %H:%M")] = df_load.iloc[n:n+1,:].squeeze()
        # next hour
        dt.append(dt[-1] + delta)
        # to ensure n does not go beyond max index
        if n>=len(df_mock):
            n = 0
        else:
            n = n + 1
        if step_count>1:
            for c in range(step_count):
                df_predict.loc[(dt[-1]+ delta*c).strftime("%Y-%m-%d %H:%M")] = pred_y[0][c]
        else:
                df_predict.loc[dt[-1].strftime("%Y-%m-%d %H:%M")] = pred_y[0]          
        col = [col for col in df_live.columns if col.split('.')[0] == 'Total Power']
        df_combined = pd.concat([df_live[col], df_predict], axis = 1, sort = True)
        # return data in a set
        datasets = {
         'df_combined': df_combined.to_json(),
         'df_current' : df_live.to_json(),
         'df_load' : df_live_load.to_json()}
        return json.dumps(datasets)


@app.callback([Output('real_apow', 'value'), Output('fc_apow_led', 'value')], 
              [Input('real_intermediate','children')])
def generate_real_time_meter (json_data):
    try:
        global phase, step_count
        datasets = json.loads(json_data)
        df_real = pd.read_json(datasets['df_current']).round(3)
        df_combined = pd.read_json(datasets['df_combined']).round(3)
        
        return df_real['Total Power'][-1], abs(df_combined['Predicted'][-step_count])
    except:
        return 140,40
    
@app.callback([Output('live_plot','figure'),Output('real_fc_score', 'children')], 
              [Input('real_intermediate','children')])
def generate_real_time_plot (json_data):
    try:
        datasets = json.loads(json_data)
        df_combined = pd.read_json(datasets['df_combined'])

        df_combined.index = pd.to_datetime(df_combined.index, errors='coerce')
        df_trunc = df_combined[df_combined.index > df_combined.index[-1] - timedelta(hours=60)].copy()

        df_t = df_combined.dropna()        
        fig = get_ts_plot(df_trunc, yaxis_label = 'Active Power [kW]', hover_mode = 'closest')        
        
        r2 = r2_score(df_t[df_t.columns[0]], df_t[df_t.columns[1]])
        rmse = np.sqrt(mean_squared_error(df_t[df_t.columns[0]], df_t[df_t.columns[1]]))
        mae = mean_absolute_error(df_t[df_t.columns[0]], df_t[df_t.columns[1]])        
        fc_p = 'Performance: r2 = {}______RMSE = {}______MAE = {}'.format(round(r2,3), round(rmse,3), round(mae,3))
        return fig, fc_p
    except:
        return [], 'Loading...'

@app.callback([Output('live_pv_plot','figure'), Output('pv_fc_score','children'), Output('pv_gauge', 'value')],
              [Input('real_intermediate','children')])
def generate_pv_plot (json_data):
    try:
        datasets = json.loads(json_data)
        df_load = pd.read_json(datasets['df_load'])
        # df_temp = df_load.dropna()
        df_load = df_load[['Power Demand','PV Production']]
        df_load.index = pd.to_datetime(df_load.index, errors='coerce')
        # df_trunc = df_combined.iloc[-60:,:].copy()
        df_trunc = df_load[df_load.index > df_load.index[-1] - timedelta(hours=60)].copy()
        fig = get_ts_plot(df_trunc, yaxis_label = 'Power [KW]')   
        pv_peak = round(get_pv_peak(df_load['PV Production']),3)
               
        # evaluate performance
        return fig, 'Note: PV is estimated based on GHI, Power Peak (past 60 days) and Real Power.', pv_peak
    except:
        return [],'Loading...', 0