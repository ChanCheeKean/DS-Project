## Main Page
import dash_core_components as dcc
import dash_html_components as html
from app import app, server
from layouts import overview_layout, analytic_layout, visual_layout, dga_layout, realtime_layout
from layouts import overview_callbacks, analytic_callbacks, visual_callbacks, dga_callbacks, realtime_callbacks

# title name
app.title = 'Grid Analytic'

##################
# horizontal tab
##################
main_tab = dcc.Tabs(
        id="main_tab_container", 
        value='overview', 
        className = 'tab_nav',
        children=[
                dcc.Tab(
                        className = 'tab_item', 
                        selected_className='is-activated', 
                        label='Overview', 
                        value='overview', 
                        children = html.Div(overview_layout.layout, className = 'tab__content')
                        ), 
                
                dcc.Tab(
                        className = 'tab_item', 
                        selected_className='is-activated', 
                        label='Visualization', 
                        value='visualization', 
                        children = html.Div(visual_layout.layout, className = 'tab__content')
                        ), 
                
                dcc.Tab(
                        className = 'tab_item', 
                        selected_className='is-activated', 
                        label='Analytic & KPI', 
                        value='analytic', 
                        children = html.Div(analytic_layout.layout, className = 'tab__content')
                        ), 
                
                dcc.Tab(
                        className = 'tab_item', 
                        selected_className='is-activated', 
                        label='DGA', 
                        value='dga', 
                        children = html.Div(dga_layout.layout, className = 'tab__content')
                        ), 
                
                dcc.Tab(
                        className = 'tab_item', 
                        selected_className='is-activated', 
                        label='Real Time Monitoring', 
                        value='real', 
                        children = html.Div(realtime_layout.layout, className = 'tab__content')
                        ), 
                ]
        )

##################
# main layout
##################
app.layout = html.Div(
        children = [html.Div(main_tab, className = 'tabs--primary frameless')], 
        className = 'page'
        )

if __name__ == '__main__':
    app.run_server(debug=False, port = 8050)
