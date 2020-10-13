import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
 
##################
#  CO2 to CO
##################
co_plot = dbc.Card([dbc.CardHeader('Carbon Dioxide to Carbon Monoxide Ratio', className = 'card_header'),
                     dcc.Loading(
                             [dcc.Graph (id = 'dga_co', style=dict(height = '250px')),
                              html.Div('Note : Ratio <3.0 indicates fault in paper', className = 'h6 text-center')],
                             type="default"),
                    ], color="dark", outline=True)
                     

##################
#  C2h2 to H2
##################
ch_plot = dbc.Card([dbc.CardHeader('Acetylene to Hydrogen Gas Ratio', className = 'card_header'),
                     dcc.Loading(
                             [dcc.Graph (id = 'dga_ch', style=dict(height = '250px')),
                              html.Div('Note : Ratio of [2,3] indicates LTC contamination', className = 'h6 text-center')],
                             type="default"),
                    ], color="dark", outline=True)
                     
                     
##################
#  O2 to N2
##################
oh_plot = dbc.Card([dbc.CardHeader('Oxygen to Dinitrogen Ratio', className = 'card_header'),
                     dcc.Loading(
                             [dcc.Graph (id = 'dga_on', style=dict(height = '250px')),
                              html.Div('Note : Decreasing ratio indicates excessive heating', className = 'h6 text-center')],
                             type="default"),
                    ], color="dark", outline=True)


##################
#  Roger Ratio and Duval Triangle
##################

gas_plot = dcc.Graph(id='gas_plot', style=dict(height = '280px'))
duval_tri = dcc.Graph(id='duval_tri', style=dict(height = '300px'))
rogers_ratio = dcc.Graph(id='rg_ratio', style=dict(height = '300px'))

# combining 3 plots
combined_plot = dbc.Card([dbc.CardHeader('Roger Ratio and Duval Triangle', className = 'card_header'),
                     html.Div(
                             [html.Div(gas_plot),
                              dbc.Row([
                                    dbc.Col(duval_tri, width = 6),
                                    dbc.Col(rogers_ratio, width = 6),
                                    ], className = 'py-1'),  
                     ]),
                    ], color="dark", outline=True)


##################
#  error LOG
##################
alerts = dbc.Alert(children = [
                        "Warning! Unusual Profile detected. Click",
                        dbc.Button(id='dga_showlog_button', children='here', className = 'button--secondary d-inline-block', n_clicks = 0), 
                        "find out more."],
                    color="danger", 
                    dismissable = True, 
                    is_open = True, 
                    id = 'alert_msg')
                     
log = dbc.Alert(color="success", dismissable = True, is_open = True, id = 'log_details')

##################
# Main Layout
##################
layout = html.Div([
        dbc.Row([
                dbc.Col(co_plot, width = 4),
                dbc.Col(ch_plot, width = 4),
                dbc.Col(oh_plot, width = 4),
                ], className = 'py-2'), 
        combined_plot,
        alerts,
        log,
        html.Div(id='dga_initial',  className = 'd-none', children = pd.DataFrame().to_json()),   
        html.Div(id='dga_intermediate',  className = 'd-none'),
        ])