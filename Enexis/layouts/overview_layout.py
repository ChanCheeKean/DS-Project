import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dtb
import pandas as pd
from utils.dash_helpers import parse_options
from datetime import datetime, timedelta

##################
# data selector
##################
variable_picker = html.Div(
                        children = [
                                html.Div('Variable: ', className = 'inputGroup__label', style = dict(display = 'inline-block')), 
                                dcc.Dropdown (id = 'overview_var', 
                                              style = dict(display = 'inline-block'), 
                                              className = 'inputGroup select', 
                                              options = parse_options({'Active Power':'P', 'Reactive Power':'Q' , 'Voltage':'V', 'Current':'I', 'THD':'Hd'}), 
                                              value = 'V')
                                ], 
                        className = 'inputGroup inline')

date_picker =  html.Div(
                            children = [
                                            html.Div(children ='Dates: ', className = 'inputGroup__label', style = dict(display = 'inline-block')), 
                                            dcc.DatePickerRange(id='overview_date-picker', 
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

submit_button = dbc.Button(id='overview_data_button', 
                           children='Display', 
                           n_clicks=0, 
                           style = dict(display = 'inline-block'),  color="primary", className = 'button--primary')

data_selector = [variable_picker, date_picker, submit_button]

##################
# Map
##################
card_map = dbc.Card([dbc.CardHeader('Grid Distribution', className = 'card_header'),
                     dcc.Graph(id = 'overview_map', config= dict(scrollZoom = True), style=dict(height = '350px'))
                    ], color="dark", outline=True)

##################
# Polar_chart
##################
polar_map = dbc.Card([dbc.CardHeader('KPI Radar Chart', className = 'card_header'),
                     dcc.Loading(
                             dcc.Graph(id = 'overview_radar', style= dict(height = '350px')),
                             type="default"),
                    ], color="dark", outline=True)
                     
##################
# ts_plot
##################
ts_plot = dbc.Card([dbc.CardHeader('Time Series Plot', className = 'card_header'),
                     dcc.Loading(
                             dcc.Graph (id = 'overview_ts', style=dict(height = '300px')),
                             type="default"),
                    ], color="dark", outline=True)
                     
##################
# box plot
##################
box_plot = dbc.Card([dbc.CardHeader('Box Plot', className = 'card_header'),
                     dcc.Loading(
                             dcc.Graph (id = 'overview_box', style=dict(height = '300px')),
                             type="default"),
                    ], color="dark", outline=True)

##################
# table
##################
table = dtb.DataTable(
    id='overview_table',
    row_selectable="multi",
    selected_rows=[],
    sort_action="native",
    style_cell = {'textAlign': 'center', 'textOverflow': 'clip',}, 
    style_table = {'minHeight': '50px', 'overflowY': 'auto', 'height': '300px',  },
    style_header={ 'textAlign': 'center', 'fontWeight': 'bold',},
    style_cell_conditional=[{'if': {'column_id': 'Station'}, 'textAlign': 'left'}],
)

table_card = dbc.Card([dbc.CardHeader('Detailed Table', className = 'card_header'),
                     dcc.Loading(
                             table,
                             type="default"),
                    ], color="dark", outline=True)


##################
# Main Layout
##################
layout = html.Div([
        html.Div(children = data_selector),
        dbc.Row([
                dbc.Col(card_map, width = 7),
                dbc.Col(polar_map, width = 5),
                ], className = 'py-2'),         
        table_card,                            
        dbc.Row([
                dbc.Col(ts_plot, width = 6),
                dbc.Col(box_plot, width = 6),
                ], className = 'py-2'), 
        html.Div(id='overview_initial',  className = 'd-none', children = pd.DataFrame().to_json()),   
        html.Div(id='overview_intermediate_data',  className = 'd-none'),
        html.Div(id='overview_intermediate',  className = 'd-none'),
        ])
