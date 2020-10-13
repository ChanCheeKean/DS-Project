# imports
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import seaborn as sns
from seaborn import color_palette
import plotly.graph_objs as go
import plotly.figure_factory as ff
import datetime
import io
import flask
import os
import json
# import resources as rsrc
# from backend import se_helper
import pandas as pd
import base64


# hard coded week number
week_no = 9

status_map = {"REF000": "REF015", "REF002": "REF008", "REF005": "REF014", "REF012": "REF009"}

global_vars = {
    'df_inputs': None,
    'df_tasks': None,
    'df_optimal': None,
    'plot_gantt': None,
    'plot_pie': None,
    'plot_energy': None,
    'filepath': ""
}


class Defaults:
    div_style = {
        'width': '60%',
        'padding-left': '20%',
        'padding-right': '20%',
        'height': '80px',
        # 'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin': '10px',
        'display': 'inline-block',
        "text-align": "center"
    }

    details_style = {
        'width': '60%',
        'padding-left': '20%',
        'padding-right': '20%',
        # 'height': '30%',
        # 'lineHeight': '60px',
        'textAlign': 'center',
        'margin': '10px'
    }

    tabs_styles = {
        'height': '44px'
    }
    tab_style = {
        'borderBottom': '1px solid #d6d6d6',
        'padding': '6px',
        'fontWeight': 'bold'
    }

    tab_selected_style = {
        'borderTop': '1px solid #d6d6d6',
        'borderBottom': '1px solid #d6d6d6',
        'backgroundColor': '#119DFF',
        'color': 'white',
        'padding': '6px'
    }


app = dash.Dash()
app.css.append_css({"external_url": "/static/{}".format('bootstrap.min.css')})
app.css.append_css({"external_url": "/static/{}".format('style.css')})
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
server = app.server

app.index_string = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <title>{%title%}</title>
     {%favicon%}
	 {%css%}
    <!-- [2] Charset UTF-8 -->
    <meta charset="utf-8" />
    <!-- [4] Responsive viewport -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
</head>

<body>
    <div class="mdsp mdsp-defaults forceDefaultElements" id="_mdspcontent">
    
        {%app_entry%}
    <header>
        {%config%}
        {%scripts%}
        {%renderer%}
    </header>
    </div>
    
<!-- MindSphere OS bar -->
    <script src="https://static.eu1.mindsphere.io/osbar/v4/js/main.min.js"></script>
    <script>
      _mdsp.init({
          appId: "_mdspcontent",
          appInfoPath: "./static/app-info.json"
      });
    </script>

</body>
</html>
'''

app.layout = html.Div([
    # Upload CSV panel
    html.Div([
        html.H1('Energy-based Mindsphere Optimized Production Scheduler (eMOPS)'),
    ]),
    html.Div(children=[
        # html.Div(html.A(html.H5('Drag & Drop or Browse a schedule file'))),
        dcc.Upload(
            id='upload-data',
            children=html.Div(html.A(html.H5('Drag & Drop or Browse a schedule file'))),
            multiple=False,
            style={
                'display': 'inline-block',
                "text-align": "center",
                'height': '60px',
                'width': '60%',
                'padding-left': '20%',
                'padding-right': '20%',
                'borderWidth': '1px',
                'borderStyle': 'dotted',
                'borderRadius': '5px',
                'textAlign': 'center',
            }
        ),
        html.Div(
            [
                dbc.Progress(id="progress", value=0, striped=True, animated=True),
            ]
        ),
        html.Div(style={'height': '20px', 'width': '20px'}),
        html.Button(
            'Optimize Schedule',
            id='button-optimize',
            n_clicks=0,
            style={'display': 'inline-block', "text-align": "center"}
        )],
        style={
            'width': '60%',
            'padding-left': '20%',
            'padding-right': '20%',
            # 'borderWidth': '1px',
            # 'borderStyle': 'solid',
            # 'borderRadius': '5px',
            'textAlign': 'center',
            'display': 'inline-block', "text-align": "center"
        }
    ),
    html.Div(style={'height': '20px'}),
    html.Details(
        [
            html.Summary("Input Schedule"),
            # html.Table(id='table-user-input'),
            dcc.Graph(id='graph-history'),
            dcc.Graph(id='graph-user-input'),
        ],
        open=True,
        id="summary-user-input",
    ),
    html.Div(style={'height': '20px'}),
    html.Div([
        dcc.Tabs(id="tabs-styled-with-inline", value='tab-1', children=[
            dcc.Tab(label='Schedule', value='tab-schedule', style=Defaults.tab_style, selected_style=Defaults.tab_selected_style),
            dcc.Tab(label='Energy', value='tab-energy', style=Defaults.tab_style, selected_style=Defaults.tab_selected_style),
            dcc.Tab(label='Costs', value='tab-costs', style=Defaults.tab_style, selected_style=Defaults.tab_selected_style),
        ], style=Defaults.tabs_styles),
        html.Div(id='tabs-content-inline')
    ]),
    html.Div(style={'height': '20px'}),
    html.Details([
        html.Summary("Optimized Schedule"),
        dbc.Table(
            id='table-optimized-schedule',
            style={
                'width': '60%',
                'padding-left': '20%',
                'padding-right': '20%'
            }
        )],
        open=False)
])


def parse_input_schedule(contents, n_rows=1000):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    # df_week = pd.read_csv(io.StringIO(decoded.decode('utf-8')), index_col=[0]).reset_index()
    df_week = pd.read_csv(r"./data/weeks/amount_per_jobtype_year_2018_week_%d.csv" % week_no, index_col=[0]).reset_index()       # todo make not hard coded
    df_week.columns = ["Task", "Amount"]
    # df_week.Task = df_week.apply(lambda x: f"Job {int(x.name) + 1}", axis=1)
    df_week.Task = df_week.Task.apply(lambda x: x[:6] if x.startswith('REF') else x)
    df_week.Task = df_week.Task.apply(lambda x: status_map[x] if x in status_map.keys() else x)

    global_vars['df_inputs'] = df_week


def parse_optimization_results():
    df_group = global_vars['df_tasks']

    # df_week = pd.read_csv(r"../data/optimization_output.csv", index_col=[0])
    df_week = pd.read_csv(r"./data/weekly_plans/amount_per_jobtype_year_2018_week_%d.csv" % week_no)    # todo make not hard coded
    # df_week = pd.read_csv(r"../../InputSchedules\OptimizationModels\OptimizationModels\weeklyOutputs/amount_per_jobtype_year_2018_week_%d.csv" % week_no)    # todo make not hard coded
    new_col_names = df_week.columns.tolist()
    new_col_names[:3] = ["Task", "Start", "Finish"]
    df_week.columns = new_col_names

    df_week["StartDate"] = pd.to_datetime(df_week.Start)
    df_week["FinishDate"] = pd.to_datetime(df_week.Finish)
    df_week["Duration"] = df_week.apply(lambda x: (x.FinishDate - x.StartDate).total_seconds() / 3600, axis=1)
    df_week.Duration[df_week.Duration < 1e-5] = 1e-5

    df_week["Task2"] = df_week.Task.apply(lambda x: x[:6] if x.startswith('REF') else x)
    df_week.Task2 = df_week.Task2.apply(lambda x: status_map[x] if x in status_map.keys() else x)
    df_week.Status = df_week.Task
    df_week.Task = df_week.Task2

    # df_week.Task2[pd.isna(df_week["Task2"])] = df_week.Task[pd.isna(df_week["Task2"])]
    # df_week["Task2"] = df_week["Task2"].fillna(df_week.Task).unique()
    df_week["TaskEnergy"] = df_week.apply(
        lambda x: x.Amount * df_group.loc[x.Task].energy_per_part if x.Amount > 0 else \
            x.Duration * df_group.loc[x.Task]["energy_per_hour"], axis=1) * 1e-6
    df_week["TaskDuration"] = df_week.apply(lambda x: x.Amount * df_group.loc[x.Task].duration_per_part / x.Duration, axis=1)

    df_week = df_week.reset_index().drop("index", axis=1)   # todo adjust later
    # df_week = df_week[:min(len(df_week), n_rows)].reset_index().drop("index", axis=1)   # todo adjust later
    global_vars['df_optimal'] = df_week


@app.callback(Output('summary-user-input', 'children'),
              [Input('upload-data', 'contents')])
def load_input_schedule(list_of_contents):
    if list_of_contents is not None:
        parse_input_schedule(list_of_contents)
        print("Done loading input")

        input_panel_style = {'display': 'inline-block', "text-align": "center"}

        _ = [advance_progress(i) for i in range(4)]

        summary_children = [
            html.Summary("Input Schedule"),
            dcc.Graph(id='graph-user-input', figure=plot_user_input(), style=input_panel_style),
            dcc.Graph(id='graph-history', figure=plot_history_data(), style=input_panel_style)
        ]

        return summary_children

@app.callback(Output("progress", "value"))
def advance_progress(n):
    return n * 25
    # success = True
    # return success


@app.callback(Output('table-optimized-schedule', 'children'),
              [Input('button-optimize', 'n_clicks')])
def do_optimize(n_clicks):
    print(f"Optimize button clicked - n_clicks: {n_clicks}")
    if n_clicks:
        parse_optimization_results()
        df_opt_results = global_vars['df_optimal']
        table_children = generate_table(df_opt_results, 10)

        render_content('tab-schedule')

        return table_children


def generate_table(dataframe, max_rows):
    return dbc.Table.from_dataframe(dataframe, float_format=".2f", header=True, striped=True, bordered=True, dark=True,
                                    columns=["Task", "Amount", "StartDate", "FinishDate", "TaskEnergy", "TaskDuration"],
                                    date_format="%b %d, %y - %H:%M:%S",
                                    style={"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})


def plot_gantt_from_df(df_week, max_rows=25):
    colors = color_palette('hls', df_week.Task.unique().size)
    fig = ff.create_gantt(df_week, group_tasks=True, index_col='Task', show_colorbar=True, colors=colors,
                          bar_width=0.2, showgrid_x=True, showgrid_y=True, height=600, width=1800,
                          title="Optimized Production Schedule")
    for i in range(len(fig["data"])):
        if not fig["data"][i]['name']:
            fig["data"][i]['showlegend']=False
        else:
            pass
    fig["layout"].update({'xaxis': {'title': 'Day '}})

    return fig


def plot_history_data():
    df_group = pd.read_csv(r"./data/per_part.csv", index_col=[0])
    global_vars['df_tasks'] = df_group

    df_scatter_plot = df_group[df_group.amount > 0.]

    trace = go.Scatter(
        x=df_scatter_plot["energy_per_part"].astype(int),
        y=(df_scatter_plot["duration_per_part"] * 3600).astype(int),
        text=df_scatter_plot.index,
        mode='markers',
        marker=dict(
            size=df_scatter_plot["amount"] * 1e-2,
            color=[f"rgb{c}" for c in sns.color_palette('hls', df_scatter_plot.shape[0])],
            sizemode='area')
    )
    layout = {
        "hovermode": 'closest',
        'width': 800,
        'height': 600,
        'xaxis': {'title': 'Energy/Job (kWh)'},
        'yaxis': {'title': 'Duration/Job (Minutes)'},
        'title': 'Summary of Job History<br>(Energy, Duration and Volume)',
    }

    fig = go.Figure(data=[trace], layout=layout)
    return fig


def plot_user_input():
    df_bar = global_vars['df_inputs'].groupby("Task")["Amount"].sum()
    df_bar = df_bar[df_bar > 0.]
    data = [dict(
        x=df_bar.index,
        y=df_bar.values,
        type='bar',
    )]
    layout = {
        "hovermode": 'closest',
        'width': 800,
        'height': 600,
        'xaxis': {'title': 'Production Jobs'},
        'yaxis': {'title': 'Amount Required'},
        'title': 'Summary of Jobs',
    }
    fig = {'data': data, 'layout': layout}
    return fig


def plot_chart(df_week):
    trace1 = {
        "x": df_week.Start,
        "y": df_week["TaskEnergy"] / df_week["Duration"],
        "line": {"shape": 'hv'},
        "mode": 'lines+markers',
        "name": 'Task Energy',
        "type": 'scatter'
    }
    trace2 = {
        "x": df_week.Start,
        "y": df_week["TaskEnergy"][df_week.Task == "Idle"] / df_week["Duration"][df_week.Task == "Idle"],
        "line": {"shape": 'hv'},
        "mode": 'lines+markers',
        "name": 'Idle Energy',
        "type": 'scatter'
    }
    layout = {
        "hovermode": 'closest',
        'width': 1800,
        'height': 600,
        'xaxis': {'title': 'Day '},
        'yaxis': {'title': 'Power (MW)'},
        'title': 'Power Consumption Distribution',
    }

    data = [trace1]
    fig = go.Figure(data=data, layout=layout)
    return fig


def plot_pie_chart(df_week):
    df_group = global_vars['df_tasks']

    df_for_pie = df_week.groupby("Task")[["Amount", "Duration", "TaskEnergy"]].sum()
    df_for_pie["HoverText"] = df_for_pie.apply(
        lambda x: f"{x.name}:\t {int(x.Amount)}" + """<br>""" + f"\u2211: {(int(x.TaskEnergy))} MWh" + """<br>""" +
                  f"Energy per piece: {int(df_group.loc[x.name]['energy_per_part'])} Wh",
        axis=1
    )

    trace1 = go.Pie(labels=df_for_pie.index, values=df_for_pie["TaskEnergy"].round(), sort=False,
                    textinfo='percent+value+label', textfont=dict(size=12), text=df_for_pie.HoverText,
                    hoverinfo='text', hole=.4, domain={"column": 0},
                    )
    trace2 = go.Pie(labels=df_for_pie[df_for_pie["Amount"]>0.].index,
                    values=df_for_pie["Amount"][df_for_pie["Amount"]>0.],
                    textinfo='percent+value+label', textfont=dict(size=12),
                    hoverinfo='value', hole=.4, domain={"column": 1}, sort=False,
                    )
    layout1 = {'showlegend': True,
               'legend':{'orientation': 'h', 'x': .23},
               'width': 1800,
               'height': 600,
               "title": "Summary of Production<br>Energy: <b>%.2f</b> MWh<br>" % (
                   30.03 #df_for_pie["TaskEnergy"].sum(),
                   # df_for_pie["Duration"].sum() * 15
               ),
               "grid": {"rows": 1, "columns": 2},
               "annotations": [
                   {
                       "font": {
                           "size": 12
                       },
                       "showarrow": False,
                       "text": "Energy<br>Consumption<br>(MWh)",
                       "x": 0.21,
                       "y": 0.5
                   },
                   {
                       "font": {
                           "size": 12
                       },
                       "showarrow": False,
                       "text": "Amount<br>Produced",
                       "x": 0.78,
                       "y": 0.5
                   }],
               }
    fig = go.Figure(data=[trace1, trace2], layout=layout1)
    return fig


@app.callback(Output('tabs-content-inline', 'children'),
              [Input('tabs-styled-with-inline', 'value')])
def render_content(tab):
    if tab == 'tab-schedule':
        return html.Div([
            dcc.Graph(figure=plot_gantt_from_df(global_vars['df_optimal']))
        ])
    elif tab == 'tab-energy':
        return html.Div([
            dcc.Graph(figure=plot_chart(global_vars['df_optimal']))
        ])
    elif tab == 'tab-costs':
        return html.Div([
            dcc.Graph(figure=plot_pie_chart(global_vars['df_optimal']))
        ],
        style={'display': 'inline-block', "text-align": "center"})
    else:
        print(f"{tab} is not in Tabs")


if __name__ == '__main__':
    app.run_server()
