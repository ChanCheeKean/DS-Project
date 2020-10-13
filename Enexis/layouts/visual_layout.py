import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import pandas as pd
from datetime import datetime, timedelta
from utils.dash_helpers import parse_options
from utils.data_importer import transformers
import numpy as np

##################
# data selector
##################

station_picker =  html.Div(
                        children = [
                                html.Div('Station: ', className = 'inputGroup__label', style = dict(display = 'inline-block')), 
                                dcc.Dropdown (
                                                id = 'vs_station_picker', 
                                                style = dict(display = 'inline-block'), 
                                                className = 'inputGroup select', 
                                                options = parse_options(transformers), 
                                                value = transformers[0])
                                        ], 
                        className = 'inputGroup inline')

variable_picker = html.Div(
                        children = [
                                html.Div('Variable: ', className = 'inputGroup__label', style = dict(display = 'inline-block')), 
                                dcc.Dropdown (id = 'vs_var', 
                                              style = dict(display = 'inline-block'), 
                                              className = 'inputGroup select', 
                                              options = parse_options({'Active Power':'P', 
                                                                                     'Reactive Power':'Q' , 
                                                                                     'Voltage':'V', 'Current':'I', 
                                                                                     'THD':'Hd'}), 
                                              value = 'V')
                                ], 
                        className = 'inputGroup inline')
        
resolution_picker = html.Div(
                            children = [
                                    html.Div('Time Resolution: ', className = 'inputGroup__label', style = dict(display = 'inline-block')), 
                                    daq.NumericInput (id = 'vs_res_value', min=0, value=1, max=60, style = dict(display = 'inline-block'), className = 'inputGroup__input'),
                                    dcc.Dropdown (id = 'vs_res_unit', 
                                                  className = 'inputGroup select', 
                                                  style = dict(display = 'inline-block'),
                                                  options = parse_options({'Minute(s)': 'T', 'Hour(s)': 'H'}),
                                                  value = 'H',),
                                            ], 
                                className = 'inputGroup inline')

date_picker =  html.Div(
                            children = [
                                            html.Div(children ='Dates: ', className = 'inputGroup__label', style = dict(display = 'inline-block')), 
                                            dcc.DatePickerRange(id='vs_date-picker', 
                                                                min_date_allowed=datetime(2017, 12, 30), 
                                                                max_date_allowed=datetime(2018, 12, 30), 
                                                                display_format = 'DD/MM/YYYY',
                                                                start_date='2018-04-01', 
                                                                end_date='2018-05-01', 
                                                                initial_visible_month = datetime(2018, 4, 1), 
                                                                style = dict(display = 'inline-block'), 
                                                                className = 'inputGroup select date-picker'),
                                            ],
                            className = 'inputGroup inline')

submit_button = dbc.Button(id='vs_data_button', children='Display', n_clicks=0, style = dict(display = 'inline-block'),  color="primary", className = 'button--primary')

data_selector = [station_picker, variable_picker, resolution_picker, date_picker, submit_button]

##################
# Timeseries plot
##################
ts_plot = dbc.Card([dbc.CardHeader('Time Series Plot', className = 'card_header'),
                     dcc.Loading(
                             dcc.Graph (id = 'vs_ts', style=dict(height = '280px')),
                             type="default"),
                    ], color="dark", outline=True)

##################
# avg plot
##################
radio_button = dcc.RadioItems(id = 'vs_avg_radio', 
                                        className = 'radioButtonWrapper p-2',
                                        options = parse_options(
                                                {'Hourly ' : 'Hour', 'Daily ' : 
                                                'Dai', 'Day of Week ' : 'Week-Dai', 
                                                'Monthly ' : 'Month',}),
                                        value='Hour'),


avg_plot = dbc.Card([dbc.CardHeader('Timely Average', className = 'card_header'),
                     html.Div(radio_button),
                     dcc.Loading(
                             dcc.Graph (id = 'vs_avg_plot', style=dict(height = '295px')),
                             type="default"),
                    ], color="dark", outline=True)

##################
# hm plot
##################
phase_picker = html.Div( 
                children = [
                        html.Div('Phase: ', className = 'inputGroup__label', style = dict(display = 'inline-block')), 
                        dcc.Dropdown (id = 'vs_hm_picker', style = dict(display = 'inline-block'), 
                                      className = 'inputGroup select', options = parse_options([1,2,3]), value = 1)
                        ], 
                className = 'inputGroup inline d-inline-block')

hm_radio =  html.Div(
                dcc.RadioItems(id = 'vs_hm_radio', 
                               className = 'radioButtonWrapper', 
                               value = 'DvH', 
                               options= parse_options({
                                       'D vs H' : 'DvH',
                                       'Mo vs D' : 'MvD',
                                       'Mo vs H' : 'MvH'
                                       }),
                                ), className = 'inputGroup inline d-inline-block')
   
hm_plot = dbc.Card([dbc.CardHeader('Heatmap Distribution', className = 'card_header'),
                    html.Div([phase_picker, hm_radio,], className = 'inputGroup inline d-inline-block p-2'),
                     dcc.Loading(
                             dcc.Graph (id = 'vs_hm', style=dict(height = '275px')),
                             type="default"),
                    ], color="dark", outline=True)                     


##################
# linear correlation hm
##################    
corr_phase = html.Div([
        html.Div('Phase: ', className = 'inputGroup__label d-inline-block'), 
        dcc.Dropdown (id = 'vs_corr_phase', 
                      style = dict(display = 'inline-block'), 
                      options= parse_options(['1', '2', '3', 'All']),
                      value = '1',
                      className = 'inputGroup select'),
                      ], 
        className = 'inputGroup inline d-inline-block')


corr_var = html.Div(children = [
        html.Div('Variable: ', className = 'inputGroup__label d-inline-block'), 
        dcc.Dropdown (id = 'vs_corr_var', 
                      style = dict(display = 'inline-block'), 
                      options = parse_options({'Active Power':'P', 'Reactive Power':'Q' , 'Voltage':'V', 'Current':'I', 'THD':'Hd', 'All':'All'}), 
                      value = 'All',
                      className = 'inputGroup select')], 
        className = 'inputGroup inline d-inline-block')

corr_hm = html.Div([
        html.Div([corr_phase, corr_var], className = 'py-2 d-inline-block'),
        dcc.Graph (id = 'corr_hm', style=dict(height = '280px'))        
        ], style=dict(width = '100%'))
              
##################
# normalized plot
##################  
norm_phase = html.Div([
        html.Div('Phase: ', className = 'inputGroup__label d-inline-block'), 
        dcc.Dropdown (id = 'vs_norm_phase', 
                      style = dict(display = 'inline-block'), 
                      options= parse_options(['1', '2', '3', 'All']),
                      value = '1',
                      className = 'inputGroup select'),
                      ], 
        className = 'inputGroup inline d-inline-block')

norm_var = html.Div(children = [
        html.Div('Variable: ', className = 'inputGroup__label d-inline-block'), 
        dcc.Dropdown (id = 'vs_norm_var', 
                      style = dict(display = 'inline-block'), 
                      options = parse_options({'Active Power':'P', 
                                               'Reactive Power':'Q' , 
                                               'Voltage':'V', 
                                               'Current':'I', 
                                               'THD':'Hd',
                                               'All' : 'All'}), 
                      value = 'All',
                      className = 'inputGroup select')], 
        className = 'inputGroup inline d-inline-block')

norm_ts = html.Div([
        html.Div([norm_phase, norm_var], className = 'py-2 d-inline-block'),
        dcc.Graph (id = 'norm_plot', style=dict(height = '280px'))        
        ])
                                                       
##################
# vertical tab
##################                    
vert_tab_layout =  html.Div(
                    dcc.Tabs(
                    id="vizualization_tabs", 
                    value='corr', 
                    vertical = True, 
                    className = 'vert_tab_nav',
                    children=[      
                            dcc.Tab(label='Linear Correlation', 
                                    value='corr', 
                                    className = 'vert_tab_item', 
                                    selected_className = 'is-activated',
                                    children = html.Div(corr_hm, className = 'vert_tab__content')),
                                    
                             dcc.Tab(label='Nomalied Ts', 
                                    value='norm_ts', 
                                    className = 'vert_tab_item', 
                                    selected_className = 'is-activated',
                                    children = html.Div(norm_ts, className = 'vert_tab__content')),
                                    
                ]), className = 'tabs--vertical')

card_vert_tab = dbc.Card([dbc.CardHeader('Detailed Visualization', className = 'card_header'),
                    vert_tab_layout,
                    ], color="dark", outline=True)    


##################
# Main Layout
##################
layout = html.Div([
        html.Div(children = data_selector),
        ts_plot,
        dbc.Row([
                dbc.Col(avg_plot, width = 6),
                dbc.Col(hm_plot, width = 6),
                ], className = 'py-2'),  
        card_vert_tab,
        html.Div(id='visual_initial',  className = 'd-none', children = pd.DataFrame().to_json()),   
        html.Div(id='visual_intermediate',  className = 'd-none'),
        ])