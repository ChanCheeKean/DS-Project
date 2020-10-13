import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dtb
import dash_daq as daq
import pandas as pd
from utils.data_importer import transformers
from utils.dash_helpers import parse_options
from datetime import datetime, timedelta

##################
# data selector
##################
station_picker =  html.Div(
                        children = [
                                html.Div('Station: ', className = 'inputGroup__label', style = dict(display = 'inline-block')), 
                                dcc.Dropdown (
                                                id = 'analytic_station', 
                                                style = dict(display = 'inline-block'), 
                                                className = 'inputGroup select', 
                                                options = parse_options(transformers), 
                                                value = transformers[0])
                                        ], 
                        className = 'inputGroup inline')
        
resolution_picker = html.Div(
                            children = [
                                    html.Div('Time Resolution: ', className = 'inputGroup__label', style = dict(display = 'inline-block')), 
                                    daq.NumericInput (id = 'analytic_res_value', min=0, value=1, max=60, style = dict(display = 'inline-block'), className = 'inputGroup__input'),
                                    dcc.Dropdown (id = 'analytic_res_unit', 
                                                  className = 'inputGroup select', 
                                                  style = dict(display = 'inline-block'),
                                                  options = parse_options({'Minute(s)': 'T', 'Hour(s)': 'H'}),
                                                  value = 'H',),
                                            ], 
                                className = 'inputGroup inline')

date_picker =  html.Div(
                            children = [
                                            html.Div(children ='Dates: ', className = 'inputGroup__label', style = dict(display = 'inline-block')), 
                                            dcc.DatePickerRange(id='analytic_date', 
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

submit_button = dbc.Button(id='analytic_button', 
                           children='Display', 
                           n_clicks=0, 
                           style = dict(display = 'inline-block'),  
                           color="primary", 
                           className = 'button--primary')

data_selector = [station_picker, resolution_picker, date_picker, submit_button]

##################
# anomalies
##################
variable_picker = html.Div(
                        children = [
                                html.Div('Variable: ', className = 'inputGroup__label', style = dict(display = 'inline-block')), 
                                dcc.Dropdown (id = 'ana_var', 
                                              style = dict(display = 'inline-block'), 
                                              className = 'inputGroup select', 
                                              options = parse_options({'Active Power':'P', 
                                                                       'Reactive Power':'Q',
                                                                       'Apparent Power':'S',
                                                                       'Voltage':'V', 
                                                                       'Current':'I', 
                                                                       'THD':'Hd', 
                                                                       }), 
                                              value = 'V')
                                ], 
                        className = 'inputGroup inline p-2')

anomal_plot = dbc.Card([dbc.CardHeader('3-Phase Unbalances Detection', className = 'card_header'),
                     variable_picker,
                     dcc.Loading(
                             dcc.Graph(id = 'anomalies_plot', style= dict(height = '300px')),
                             type="default"),
                    ], color="dark", outline=True)
       
##################
# voltage excursion
##################
vex_input = html.Div(
                children = [
                        html.Div('MA Window (Days): ', className = 'inputGroup__label d-inline-block'), 
                        daq.NumericInput (
                                id = 'vex_ma_range', 
                                min=1, 
                                value= 10, 
                                max = 60, 
                                className = 'inputGroup__input d-inline-block')
                        ],
                className = 'inputGroup inline d-inline-block pt-2')

                     
vex_plot = dbc.Card([dbc.CardHeader('Voltage Excursion (%)', className = 'card_header'),
                     vex_input,
                     dcc.Loading(
                             dcc.Graph(id = 'vex_plot', style= dict(height = '260px')),
                             type="default"),
                    ], color="dark", outline=True)

##################
# power factor
##################    
pf_plot = dbc.Card([dbc.CardHeader('3-Phase Power Factor Ratio', className = 'card_header'),
                     dcc.Loading(
                             dcc.Graph(id = 'pf_plot', style= dict(height = '300px')),
                             type="default"),
                    ], color="dark", outline=True)                     

##################
# Rolling Correlation of Power
##################    
roll_step = html.Div(
                children = [
                        html.Div('Rolling Steps: ', className = 'inputGroup__label d-inline-block'), 
                        daq.NumericInput (
                                id = 'rolling_step', 
                                min=1, 
                                value= 10, 
                                max = 60, 
                                className = 'inputGroup__input d-inline-block')
                        ],
                className = 'inputGroup inline d-inline-block pt-2')
                     
                     
roll_corr_plot = dbc.Card([dbc.CardHeader('Apparent Power vs Current Rolling Correlation', className = 'card_header'),
                    roll_step,
                    dcc.Loading(
                             dcc.Graph(id = 'roll_corr_plot', style= dict(height = '280px')),
                             type="default"),
                    ], color="dark", outline=True)  

##################
# Main Layout
##################
layout = html.Div([
        html.Div(children = data_selector),
        anomal_plot,
        dbc.Row([
                dbc.Col(vex_plot, width = 6),
                dbc.Col(pf_plot, width = 6),
                ], className = 'py-2'), 
        
        dbc.Row([
                dbc.Col(roll_corr_plot, width = 6),
                ], className = 'py-2'),
        html.Div(id='analytic_intermediate',  className = 'd-none'),
        ])