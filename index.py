#%%
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
# Connect to main app.py file
from app import app, server

# Connect to your app pages
from apps import choropleth, construction

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('Choropleth', href='/heat-map', className='button'),
        dcc.Link('Dashboard', href='/dashboard', className='button')
    ]),
    html.Div(id='page-content')
])


@app.callback(Output(component_id='page-content', component_property='children'),
              [Input(component_id='url', component_property='pathname')])
def display_page(pathname):
    if pathname == '/heat-map':
        return choropleth.layout
    elif pathname == '/dashboard':
        return construction.layout
    else:
        return construction.layout


if __name__ == '__main__':
    app.run_server(debug=True)
# %%
