#%%
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
# Connect to main app.py file
from app import app, server

# Connect to your app pages
from apps import choropleth, construction

layouts = {'/heat-map': choropleth.layout,
          '/': construction.layout,
          '/dashboard': construction.layout}

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    html.Div([
        html.Div([
                dcc.Link(
                    html.Img(src=app.get_asset_url('va.png'), style={'height':'56px'},
                         className='w3-cell w3-bar-item w3-hover-blue'), href='/'),
                dcc.Link('Choropleth', href='/heat-map', style={'height':'56px', 
                                                                'text-decoration':'none',
                                                                'text-shadow':'0.5px 0.5px 0 #444'},
                         className='w3-cell w3-bar-item w3-hover-blue'),
                dcc.Link('Dashboard', href='/dashboard', style={'height':'56px',
                                                             'text-decoration':'none', 
                                                             'text-shadow':'0.5px 0.5px 0 #444'},
                         className='w3-bar-item w3-hover-blue')
        ], className='w3-container w3-white w3-bar w3-card')
    ], className='w3-top'),

    html.Div(id='page-content', className='w3-container w3-padding-48')
])


@app.callback(Output(component_id='page-content', component_property='children'),
              [Input(component_id='url', component_property='pathname')])
def display_page(pathname):
    return layouts[pathname]


if __name__ == '__main__':
    app.run_server(debug=True)
# %%
