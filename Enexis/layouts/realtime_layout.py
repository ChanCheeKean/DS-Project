import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

##################
# gauge
##################
real_power_gauge = daq.Gauge(color={"gradient":True,"ranges":{"gold":[0,100],"green":[100,130],"red":[130,150]}},
                            label='Total Active Power', showCurrentValue=True, units = 'kW',
                            scale={'start': 0, 'interval': 25, 'labelInterval': 1}, size = 160, className = 'gauge',
                            max=150, min=0, id = 'real_apow', labelPosition = 'top',
                            style=dict(display = 'inline-block', height = '80px'),)

pv_gauge = daq.Gauge(    color={"gradient":True,"ranges":{"green":[0,500],"gold":[500,1200],"red":[1200,1500]}},
                            label='Peak Daily PV Production', showCurrentValue=True, units = 'kWh',
                            scale={'start': 0, 'interval': 250, 'labelInterval': 1}, size = 160, className = 'gauge',
                            max=1500, min=0, id = 'pv_gauge', labelPosition = 'top',
                            style=dict(display = 'inline-block', height = '80px'),)

fc_power_led = daq.LEDDisplay( id='fc_apow_led', label="Next Forecasted Value", value=30.538, size=20, color = '#7567f5',
                                  labelPosition = 'bottom', className = 'gauge')

on_button = daq.PowerButton(id='on_button', size=60, on = True, label = ' ', labelPosition = 'top', color= '#55f4e2')

                              
real_input = [  
                html.Div([html.Div('Forecast Steps: ', className = 'inputGroup__label d-inline-block'), 
                            daq.NumericInput (id = 'real_step', min=1, value=6, max=12, className = 'inputGroup__input d-inline-block')],
                            className = 'inputGroup inline d-inline-block'), 
                                      
                dbc.Button(id='show_button', children='Forecast', n_clicks=0, className = 'button--primary d-inline-block'),                              
                ]                         

##################
# live plot
##################
live_plot = [dcc.Graph(id='live_plot', style= dict(height = '240px')), 
             html.Div(real_input, className = 'pr-5', style = dict(display = 'inline-block')),
             html.Div(id='real_fc_score', children = 'Loading...', className = 'h6', style = dict(display = 'inline-block')),
             ]

pv_plot = [dcc.Graph(id='live_pv_plot', style= dict(height = '250px')), 
                    html.Div(id='pv_fc_score', children = 'Loading...', className = 'h6')]

power_plot = [dcc.Graph(id='power_plot', style= dict(height = '225px'))]


##################
# Main Layout
##################
layout = html.Div([
                    on_button,
                    dbc.Row([
                        dbc.Col(html.Div([html.Div(real_power_gauge, className = 'pb-3'), 
                                          html.Div(fc_power_led, className = 'pt-5 pr-4')], className = 'graph_container gauge_box p-1'), width=3,),
                        dbc.Col(html.Div(live_plot, className = 'graph_container p-1'), width=9,),
                    ], className = 'pt-2'),

                    dbc.Row([
                        dbc.Col(html.Div(pv_gauge, className = 'graph_container gauge_box pt-4'), width=3,),
                        dbc.Col(html.Div(pv_plot, className = 'graph_container p-1'), width=9,),
                    ], className = 'pt-2'),

                    dcc.Interval(id='real_interval_comp', interval=5*1000, n_intervals=0),
                    html.Div(id='real_int_data', style= dict(display = 'none')),
                    html.Div(id='real_intermediate', style= dict(display = 'none')),
                    ])