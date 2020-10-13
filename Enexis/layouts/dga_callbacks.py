# Layout for forecasting page
from dash.dependencies import Input, Output, State
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from app import app
from utils.rest_helper import read_files
from utils.graph_helpers import get_ts_plot
from datetime import datetime, timedelta

# import data
@app.callback(Output('dga_intermediate','children'), 
              [Input('dga_initial','children')])
def import_data(json_data):
    df_gas = pd.read_csv('./data/additional/gas_data.csv', index_col = 0)
    df_gas.index = pd.to_datetime(df_gas.index)
    return df_gas.to_json()

# co2/co ratio plot
@app.callback([Output('dga_co','figure'), 
               Output('dga_ch','figure'),
               Output('dga_on','figure'),
               Output('log_details', 'children')],
              [Input('dga_intermediate','children')])
def update_co_ratio_graph(json_data):
   try:
       #ratio
       df_gas = pd.read_json (json_data)
    
       # CO2/CO figure        
       df_r1 =  pd.DataFrame ({
               'CO2/CO' : df_gas['CO2'] / df_gas['CO'],
               'th' : 3.0,
               })
       df_r1.replace([np.inf, np.nan],0, inplace = True)
       fig_co = get_ts_plot(df_r1, yaxis_label = '', convert_x = False, legend_bool = False)
       
       # C2H2/H2 ratio plot
       df_r2 = pd.DataFrame ({
               'C2H2/H2' : df_gas['C2H2'] / df_gas['H2'],
               'low_th' : 2.0,
               'high_th' : 3.0 ,
               })
       df_r2.replace([np.inf, np.nan],0, inplace = True)
       fig_ch = get_ts_plot(df_r2, yaxis_label = '', convert_x = False, legend_bool = True)
       
       # O2/N2 ratio plot
       df_r3 = pd.DataFrame ({
               'O2/N2' : df_gas['O2'] / df_gas['N2']
               })
       df_r3.replace([np.inf, np.nan],0, inplace = True)
       fig_on = get_ts_plot(df_r3, yaxis_label = '', convert_x = False, legend_bool = False)
       
       
       # error log details
       report = [html.H2('Analytic Result for DGA', className = 'test-center'),] 
       # for CO
       for i in df_r1[df_r1['CO2/CO']<3].index.tolist():
           report.append(
                    html.Div('[{}]: Paper Fault (CO2/CO ratio)'.format(i),))
       # for C2H2/H2
       for i in df_r2[(df_r2['C2H2/H2']>2) & (df_r2['C2H2/H2']<3)].index.tolist():
           print (i)
           report.append(
                    html.Div('[{}]: LTC Contamination (C2H2/H2 ratio)'.format(i),))
       # for O2/N2
       df_r3['decreasing'] = np.nan
       for i in range(len(df_r3)):
            x = df_r3.iloc[i:i+4,0]
            if ((x.empty) | (x.mean() == 0)):
                df_r3.iloc[i,-1] = np.nan
            else:
                 df_r3.iloc[i,-1] = x.is_monotonic_decreasing
                 
        # for C2H2/H2
       for i in df_r3[df_r3['decreasing'].diff() == 1].index.tolist():
           print (i)
           report.append(
                    html.Div('[{}]: Excessive Heating (Decreasing O2/N2 ratio)'.format(i),))
       
       return fig_co, fig_ch, fig_on, report
   except:
       return [], [], [], []
   

# collapsible log
@app.callback(Output('log_details','is_open'), 
              [Input('dga_showlog_button','n_clicks')],
              [State('log_details','is_open')])
def collapse_log(n_clicks, on):
    return not on

# time series plot for 5 gaseous
@app.callback(Output('gas_plot','figure'), [Input('dga_intermediate','children')])
def update_gas_graph(json_data):
   try:
        df_gas = pd.read_json (json_data)
        df_gas = df_gas [['CH4', 'C2H2', 'C2H4', 'C2H6','H2']]
        # plotting
        fig = get_ts_plot(df_gas, yaxis_label = 'ppm', convert_x = False, drag_mode = 'select')
        return fig
   except:
        return []

# duval_triangle
@app.callback(Output('duval_tri','figure'), 
              [Input('dga_intermediate','children'), Input('gas_plot', 'selectedData')])
def update_duval_tri(json_data, selectedData):
   try:
        df_gas = pd.read_json (json_data)
        df_gas = df_gas [['CH4', 'C2H2', 'C2H4']]
        try:
            df_gas = df_gas [df_gas.index > selectedData['range']['x'][0]]
            df_gas = df_gas [df_gas.index < selectedData['range']['x'][1]]
        except:
            pass
        
        df_ratio = df_gas.div (df_gas.sum(axis=1), axis = 0).round(4)
        fig = get_duval(df_ratio)
        return fig
   except:
        return []

# duval triangle function
def get_duval (df_ratio):
        trace0 = go.Scatterternary( a = [98, 1, 98], b = [0, 0, 2], c = [2, 0, 0], fill = "toself", fillcolor = "#8dd3c7", 
                                line = dict (color =  "#444"), mode = "lines", text = 'PD Partial Discharge', name = 'Partial Discharge', hoverinfo = 'text')
                                             
        trace1 = go.Scatterternary( a = [0, 0, 64, 87], b = [1, 77, 13, 13], c = [0, 23, 23, 0], fill = "toself", fillcolor = "#ffffb3", 
                                    line = dict (color =  "#444"), mode = "lines", text = 'D1 Discharge of Low Energy', name = 'Thermal Fault T > 700°C', 
                                    hoverinfo = 'text')  
                                                 
        trace2 = go.Scatterternary( a = [0, 0, 31, 47, 64], b = [77, 29, 29, 13, 13], c = [23, 71, 40, 40, 23], fill = "toself", fillcolor = "#bebada", 
                                    line = dict (color =  "#444"), mode = "lines", text = 'D2 Discharge of High Energy', 
                                    name = 'Discharge of High Energy', hoverinfo = 'text')   
                                                 
        trace3 = go.Scatterternary( a = [0, 0, 35, 46, 96, 87, 47, 31], b = [29, 15, 15, 4, 4, 13, 13, 29], c = [71, 85, 50, 50, 0, 0, 40, 40], 
                                    fill = "toself", fillcolor = "#fb8072", line = dict (color =  "#444"), 
                                    mode = "lines", text = 'DT Electrical and Thermal Fault', name = 'Electrical and Thermal Fault', hoverinfo = 'text')
        
        trace4 = go.Scatterternary( a = [76, 80, 98, 98, 96], b = [4, 0, 0, 2, 4], c = [20, 20, 2, 0, 0], fill = "toself", fillcolor = "#80b1d3", 
                                    line = dict (color =  "#444"), mode = "lines", text = 'T1 Thermal Fault < 300°C', 
                                    name = 'Thermal Fault < 300°C', hoverinfo = 'text') 
                                                 
        trace5 = go.Scatterternary( a = [46, 50, 80, 76], b = [4, 0, 0, 4], c = [50, 50, 20, 20], fill = "toself", fillcolor = "#fdb462", 
                                    line = dict (color =  "#444"), mode = "lines", text = 'T2 Thermal Fault 300 < T < 700°C', 
                                    name = 'Thermal Fault 300 < T < 700°C', hoverinfo = 'text')
                                                 
        trace6 = go.Scatterternary( a = [0, 0, 50, 35], b = [15, 0, 0, 15], c = [85, 1, 50, 50], fill = "toself", fillcolor = "#b3de69", 
                                    line = dict (color =  "#444"), mode = "lines", text = 'T3 Thermal Fault > 700°C', 
                                    name = 'Thermal Fault > 700°C', hoverinfo = 'text')
        f1 = df_ratio.iloc[:,0].copy()
        f2 = df_ratio.iloc[:,1].copy()
        f3 = df_ratio.iloc[:,2].copy()     
        text = [ f1[k:k+1].index[0].strftime("%d-%b-%Y %H:%M") + '<br>CH4: '+'{}'.format(f1[k])+'<br>C2H2: '+'{}'.format(f2[k])+'<br>C2H4: '+'{}'.format(f3[k]) for k in range(len(f1))]
        f1 = f1.apply(lambda x: x + 0.01 if x < 0.1 else x)
        f2 = f2.apply(lambda x: x + 0.01 if x < 0.1 else x)
        f3 = f3.apply(lambda x: x + 0.01 if x < 0.1 else x)
        trace7 = go.Scatterternary( a = f1, b = f2, c = f3, hoverinfo='text', text=text,
                                     marker = dict (color =  "red", size = 8, symbol = 28), mode = "markers", name = 'Data Points')
        data = [trace0, trace1, trace2, trace3, trace4, trace5, trace6, trace7]
        layout = go.Layout( autosize = True, showlegend = True, legend = dict(x = 0.9, y = 1, font = dict(size = 8)),
                               ternary = dict ( 
                                        aaxis = dict( linewidth = 2, min = 0.01, ticks = "outside", 
                                                     ticksuffix = "%", title = "CH4(Methane)", titlefont = dict(color = '#0e4886')), 
                                        baxis = dict( linewidth = 2, min = 0.01, ticks = "outside", 
                                                     ticksuffix = "%", title = "C2H2(Acetylene)", titlefont = dict(color = '#0e4886')), 
                                        caxis = dict( linewidth = 2, min = 0.01, ticks = "outside", 
                                                     ticksuffix = "%", title = "C2H4(Ethylene)", titlefont = dict(color = '#0e4886')), 
                                        sum = 100), 
                                        margin = dict(l = 0, r = 0, t = 55, b = 35),
                                font = dict(size = 10), titlefont = dict(size = 14, color = '#0e4886'))
        fig_tri = go.Figure(data=data, layout=layout)
        return fig_tri

# roger ratio
@app.callback(Output('rg_ratio','figure'), 
              [Input('dga_intermediate','children'), Input('gas_plot', 'selectedData')])
def update_rogers_ratio(json_data, selectedData):
 
        df_gas = pd.read_json (json_data)
        try:
            # aggregate data based on selected ts
            df_gas = df_gas [df_gas.index > selectedData['range']['x'][0]]
            df_gas = df_gas [df_gas.index < selectedData['range']['x'][1]]
        except:
            pass
        df_ratio = pd.DataFrame()
        df_ratio ['C2H4/C2H6'] = df_gas['C2H4']/df_gas['C2H6']
        df_ratio ['CH4/H2'] = df_gas['CH4']/df_gas['H2']
        df_ratio ['C2H2/C2H4'] = df_gas['C2H2']/df_gas['C2H4']
        df_ratio.replace([np.inf, -np.inf, np.nan], 0, inplace = True)
        fig = get_roger_3d(df_ratio)
        return fig

#  roger function
def get_surface(xmax, xmin, ymax, ymin, zmax, zmin, s = 's1', color = 'red', name = 'D1'):
    
    if s == 's1':
        surf = go.Mesh3d(x= [xmin, xmax, xmax, xmin], 
                         y= [ymin, ymin, ymax, ymax], 
                         z= [zmin, zmin, zmin, zmin], 
                         opacity = 0.5,
                         color = color,
                         text = name,
                         hoverinfo = 'text')
    elif s == 's2':
        surf = go.Mesh3d(x= [xmin, xmax, xmax, xmin], 
                         y= [ymin, ymin, ymax, ymax], 
                         z= [zmax, zmax, zmax, zmax], 
                         opacity=0.5,
                         color = color,
                         text = name,
                         hoverinfo = 'text')
    elif s == 's3':
        surf = go.Mesh3d(x= [xmin, xmax, xmax, xmin], 
                         y= [ymin, ymin, ymin + .001, ymin + .001],
                         z= [zmax, zmax, zmin, zmin], 
                         opacity=0.5,
                         color = color,
                         text = name,
                         hoverinfo = 'text')
    elif s == 's4':
        surf = go.Mesh3d(x= [xmin, xmax, xmax, xmin], 
                         y= [ymax, ymax, ymax + .001, ymax + .001],
                         z= [zmax, zmax, zmin, zmin], 
                         opacity=0.5,
                         color = color,
                         text = name,
                         hoverinfo = 'text')

    elif s == 's5':
        surf = go.Mesh3d(x= [xmin, xmin, xmin + .001, xmin + .001], 
                         y= [ymin, ymax, ymax, ymin],
                         z= [zmax, zmax, zmin, zmin], 
                         opacity=0.5,
                         color = color,
                         text = name,
                         hoverinfo = 'text')
        
    elif s == 's6':
        surf = go.Mesh3d(x= [xmax, xmax, xmax + .001, xmax + .001], 
                         y= [ymin, ymax, ymax, ymin],
                         z= [zmax, zmax, zmin, zmin], 
                         opacity=0.5,
                         color = color,
                         text = name,
                         hoverinfo = 'text')
    return surf

#  roger function
def get_roger_3d (df_ratio):
    data = []
        
    # PD
    for i in range(1,7):
        trace = get_surface(0, 0.2, 0, 0.1, 0, 4, s = 's' + str(i), color = '#8dd3c7', name = 'PD Partial Discharge')
        data.append(trace)
        
    # d1
    for i in range(1,7):
        trace = get_surface(1, 6, 0.1, 0.5, 1, 4, s = 's' + str(i), color = '#ffffb3',name = 'D1 Discharge of Low Energy')
        data.append(trace)
            
    # d2
    for i in range(1,7):
        trace = get_surface(2, 6, 0.1, 1, 0.6, 2.5, s = 's' + str(i), color = '#bebada', name = 'D2 Discharge of High Energy')
        data.append(trace)
            
    # t1
    for i in range(1,7):
        trace = get_surface(0, 1, 0, 2, 0, 4, s = 's' + str(i), color = '#80b1d3', name = 'T1 Thermal Fault < 300°C')
        data.append(trace)
        
    # t2
    for i in range(1,7):
        trace = get_surface(1, 4, 1, 2, 0, 0.1, s = 's' + str(i), color = '#fdb462', name = 'T2 Thermal Fault 300 < T < 700°C')
        data.append(trace)
        
    # t3
    for i in range(1,7):
        trace = get_surface(4, 6, 1, 2, 0, 0.2, s = 's' + str(i), color = '#b3de69', name = 'T3 Thermal Fault > 700°C')
        data.append(trace)
        
    # for scatter point
    f1 = df_ratio.iloc[:,0].round(2)
    f2 = df_ratio.iloc[:,1].round(2)
    f3 = df_ratio.iloc[:,2].round(2)     
    text = [ f1[k:k+1].index[0].strftime("%d-%b-%Y %H:%M") + '<br>CH4: '+'{}'.format(f1[k])+'<br>C2H2: '+'{}'.format(f2[k])+'<br>C2H4: '+'{}'.format(f3[k]) for k in range(len(f1))]
    trace = go.Scatter3d( x = f1, y = f2, z = f3, 
                         hoverinfo='text', text=text, mode='markers',
                         marker=dict( size= 5, color='red'))
    data.append(trace)
    
    layout = go.Layout( 
                scene = dict(
                        xaxis = dict(nticks=6, range=[0,6], 
                                     title = "C2H4 / C2H6", 
                                     tickfont = dict(size=10), 
                                     linewidth= 3, 
                                     linecolor='black',
                                     mirror=True,
                                     gridwidth=1, 
                                     gridcolor='black',
                                     titlefont = dict(color = '#0e4886', size=10)),
                        yaxis = dict(nticks=4, range=[0,2], 
                                     title = "CH4 / H2", 
                                     tickfont = dict(size=10), 
                                     linewidth= 3, 
                                     linecolor='black',
                                     mirror=True,
                                     gridwidth=1, 
                                     gridcolor='black',
                                     titlefont = dict(color = '#0e4886', size=10)),
                        zaxis = dict(nticks=4, 
                                     range=[0,4], 
                                     title = "C2H2 / C2H4", 
                                     tickfont = dict(size=10), 
                                     linewidth= 3, 
                                     linecolor='black',
                                     mirror=True,
                                     gridwidth=1, 
                                     gridcolor='black',
                                     titlefont = dict(color = '#0e4886', size=10)),
                        ),
                font = dict(size = 10), 
                titlefont = dict(size = 14, color = '#0e4886'),        
                margin=dict(r=5, l=5, b=5, t=55),
                showlegend = False,
                legend = dict(x = 0.9, y = 1, font = dict(size = 8))
                )
    fig = go.Figure(data=data, layout=layout)
    return fig