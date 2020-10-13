# Layout for forecasting page
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from app import app
from utils.data_importer import transformers, get_reading, get_channel, get_phase
from utils.graph_helpers import get_ts_plot, get_box_plot
from datetime import datetime
import json

# generate data
@app.callback (Output('overview_intermediate', 'children'),
               [Input('overview_initial', 'children')])
def generate_data(n):
    # import location
    df_loc = pd.read_csv('./data/location/transformer_location.csv', index_col = 0)
    # generate random radar data dor each stations
    df_radar = pd.DataFrame(columns = ["Power Factor", "Unbalances", "Power Load", "Consistency"])
    for station in transformers:
        df_radar.loc[station] = np.random.randint(1,11, size= 4).tolist()
    # store data as json
    datasets = {
         'df_loc': df_loc.to_json(),
         'df_radar' : df_radar.to_json()}
    return json.dumps(datasets)

# generate mapbox
@app.callback (Output('overview_map', 'figure'), 
               [Input('overview_intermediate', 'children')])
def generate_mapbox(json_data):
    # call data
    datasets = json.loads(json_data)
    df_loc = pd.read_json(datasets['df_loc'])    
    
    # plotting
    fig = get_mapbox(
            df = df_loc, 
            lat = df_loc['Lat'], 
            lon = df_loc['Lon'], 
            text = df_loc['transformer'], 
            center_lat = df_loc['Lat'].mean(), 
            center_lon = df_loc['Lon'].mean(), 
            zoom = 6.5)
    return fig
# mapbox function
def get_mapbox(df, lat, lon, text, center_lat = 0, center_lon = 0, zoom = 2):            
        mapbox_access_token = "pk.eyJ1IjoiY2hhbmNoZWVrZWFuIiwiYSI6ImNqdjgzYmYzNjBmeDQzem43MzIwcnI1djMifQ.igdgIdtTUOVIAXO7WA2ZBw" 
        data = [go.Scattermapbox(lat = lat, lon = lon, text = text, hoverinfo = 'text',marker = dict(size = 12, color = 'red'))]
        
        layout = go.Layout(
                autosize=True, 
                showlegend = False,
                hovermode='closest', 
                dragmode = 'select', 
                clickmode = 'event+select',
                margin = dict(l = 0, r = 0, t = 0, b = 0),
                font = dict(size = 10),
                mapbox=dict( accesstoken=mapbox_access_token, bearing = 0, style = 'outdoors',
                center=dict( lat = center_lat, lon = center_lon), pitch=0, zoom = zoom)
                )
        fig = go.Figure(data=data, layout=layout)
        return fig
    
    
# radar chart
@app.callback (Output('overview_radar', 'figure'),  
               [Input('overview_intermediate', 'children'), Input('overview_map', 'selectedData')]
               )
def update_radar (json_data, selectedData):
    
    # call data
    datasets = json.loads(json_data)
    df_radar = pd.read_json(datasets['df_radar'])
    theta = np.append(df_radar.columns.values, df_radar.columns[0])
    
    # plotting
    try:
        stations = [data['text'] for data in selectedData['points']]
        
        data = []
        for station in stations:
            df_temp = df_radar[theta][df_radar.index == station]
            trace1 = go.Scatterpolar(
                    r = df_temp.values.tolist()[0], 
                    theta = theta, mode = 'markers + lines', 
                    name = station
                    )
            data.append(trace1)
    except:
        data = [go.Scatterpolar(
                r = [1,1,1,1,1,1], 
                theta = theta, 
                mode = 'markers + lines')
    ]
    layout = go.Layout (
                        polar = dict(
                                radialaxis = dict(visible=True, range=[0, 10]), 
                                angularaxis_categoryarray = df_radar.columns.values,
                                ),
                        legend_orientation = 'h',
                        legend = dict(x = 0, y = 1.4, font = dict(size = 8)),
                        showlegend = True, 
                        font = dict(size = 8), 
                        margin = dict(l = 5, r = 5, t = 45, b = 30)
                        )
    fig = go.Figure (data = data, layout = layout)
    return fig


# generate transformer data according to selected stations
@app.callback (
        Output('overview_intermediate_data', 'children'),
        [Input('overview_data_button','n_clicks'), Input('overview_map', 'selectedData')], 
        [State('overview_var', 'value'), State('overview_date-picker', 'start_date'), 
         State('overview_date-picker', 'end_date')])
def update_data_intermediate(n_clicks, selectedData, var, start, end):
    try:
        # list of selected stations
        stations = [data['text'] for data in selectedData['points']]
    
        # import data according to selected stations
        df_target = pd.DataFrame()
        for station in stations:
            df = get_reading(station_name = station)
            df = get_channel(df,var)
            df = df[(df.index >= start) & (df.index <= end)]
            df.columns = station + '__' + df.columns
            df_target = pd.concat([df_target, df], axis = 1, sort = True)
        return df_target.to_json()
    except:
        return []


# dash table
@app.callback (
        [Output('overview_table', 'columns'), Output('overview_table', 'data'), 
         Output('overview_table', 'selected_rows'), Output('overview_table', 'filter_action')],   
        [Input('overview_intermediate_data', 'children')])    
            
def gen_table_data(json_data):
    try: 
        df = pd.read_json(json_data)  

        # impute statistical parameters for each variables
        df_table = pd.DataFrame(
                        columns = ['Station','Variable (phase)', 'Min', 'Mean', 'Max', 'Std'],
                        data = {
                                    'Station': [col.split('__')[0] for col in df.columns],
                                    'Variable (phase)': [col.split('__')[-1] for col in df.columns],   
                                    'Mean': df.mean(),
                                    'Min' : df.min(),
                                    'Max' : df.max(),
                                    'Std' : df.std(),
                        })    
        df_table = df_table.reset_index(drop = True)
        df_table = df_table.round(3)
        
        # return dataframe in dash table format
        columns = [{"name": i, "id": i} for i in df_table.columns]
        data = df_table.to_dict('records')
        return columns, data, [], 'native'
    
    # show emtpy table with columns name if no data is selected
    except:
        df_table = pd.DataFrame(columns = ['Station','Variable (phase)', 'Min', 'Mean', 'Max', 'Std'])
        return [{"name": i, "id": i} for i in df_table.columns], [], [], 'native'

# time series
@app.callback (
        [Output('overview_ts', 'figure'), Output('overview_box', 'figure')], 
        [Input('overview_table', "derived_virtual_data"), Input('overview_table', 'derived_virtual_selected_rows')],
        [State('overview_intermediate_data', 'children')])
def update_tsbox_graph (rows, selectedRows, json_data):
    try:
        # call data according to selected station
        df = pd.read_json(json_data)
        df_selected = pd.DataFrame(rows).loc[selectedRows]
                
        df_selected['target'] =  df_selected['Station'] + '__' +df_selected ['Variable (phase)']
        df = df[[col for col in df.columns if col in df_selected['target'].unique()]]
        
        # plotting
        fig_ts = get_ts_plot(df, yaxis_label = ' ', convert_x = False, xaxis_label = ' ')
        fig_box = get_box_plot(df, y_label = ' ')
        return fig_ts, fig_box
    except:
        return [], []
