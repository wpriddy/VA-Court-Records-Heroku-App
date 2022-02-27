#%%
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
from itertools import product
import sys
sys.path.insert(0, r'..')
from app import app
import plotly.express as px
import pandas as pd
import pathlib
from data.get_data import *

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data/files").resolve()

colors = {
    'background': '#111111',
    'text': '#2C2C2C'
}

fips_map = pd.read_pickle(DATA_PATH.joinpath('fips_map.pickle'))

layout = html.Div(children = [

    dcc.ConfirmDialog(
        id = 'insufficient-data',
        message = "{} Insufficient Data Available. Set Another Breakout {}".format(u"\u26A0", u"\u26A0")
    ),

    html.H1(children = 'Virginia Court Records Interactive Dashboard',
            style = {
                'textAlign': 'center',
                'color': colors['text'],
                'font-weight': 'bold',
                'margin-top': '20px'                 
            }),

    html.Div([
            html.Div(
                dcc.Dropdown(
                    id='district_or_circuit_d',
                    options = [{'label': 'Circuit', 'value': 'circuit'}, {'label': 'District', 'value': 'district'}],
                    value = 'circuit',
                    searchable=False, 
                    style={'background-color': '#DDD7D7','width': '100%'},
                    className = 'row',
                    placeholder = 'Select a Court'
                ), style={'width': '16%', 'display': 'inline-block'}),

            html.Div(' a'*2,  style={'color':'white'}),

            html.Div(
                dcc.Dropdown(
                    id='fips_code',
                    options = [{'label': val, 'value': key} for key, val in sorted(fips_map.items(), key=lambda item: item[1])],
                    value = 'All',
                    searchable=False,
                    multi=True,
                    style={'background-color': '#DDD7D7','width': '100%'},
                    className = 'row',
                    placeholder = 'All Regions'
                ), style = {'width': '16%', 'display': 'inline-block'}),

            html.Div(' a'*2,  style={'color':'white'}),

            html.Div(
                dcc.Dropdown(
                    id='race_d',
                    options=[{'label': val, 'value': key} for key, val in sorted(race_map.items(), key=lambda item: item[1]) if val != 'Unknown'],
                    value= [5],
                    searchable=False,
                    multi=True,
                    style={'background-color': '#DDD7D7','width': '100%'},
                    className = 'row',
                    placeholder = 'All Races'
                ), style = {'width': '16%', 'display': 'inline-block'}),
            
            html.Div(' a'*2,  style={'color':'white'}),

            html.Div(
                dcc.Dropdown(
                    id='gender_d',
                    options = [{'label': val, 'value': key} for key, val in sorted(sex_map.items(), key=lambda item: item[1])],
                    value = [1],
                    searchable=False,
                    multi=True, 
                    style={'background-color': '#DDD7D7','width': '100%'},
                    className = 'row', 
                    placeholder = 'All Sexes'
                ), style = {'width': '16%', 'display': 'inline-block'}),

               html.Div(' a'*2,  style={'color':'white'}),
        
                html.Div(
                    dcc.Dropdown(
                        id='charge_type_d',
                        options = [{'label': val, 'value': key} for key, val in sorted(charge_map['circuit'].items(), key=lambda item: item[1])],
                        value = [0],
                        searchable=False,
                        multi=True, 
                        style={'background-color': '#DDD7D7','width': '100%'},
                        className = 'row',
                        placeholder = 'All Charges'
                    ), style =  {'width': '16%', 'display': 'inline-block'}),
                    
                html.Div(' a'*2,  style={'color':'white'}),

                html.Div(
                    dcc.Dropdown(
                        id='disposition_type_d',
                        options = [{'label': val, 'value': key} for key, val in sorted(dispo_map['circuit'].items(), key=lambda item: item[1])],
                        value = [0],
                        searchable=False,
                        multi=True,
                        style={'background-color': '#DDD7D7','width': '100%'},
                        className = 'row',
                        placeholder = 'All Dispositions'
                    ), style =  {'width': '16%', 'display': 'inline-block'}),

                ], style={'display':'flex', 'margin':'1.5em'}
    ),
        html.Div([

            html.Div(html.Img(src=app.get_asset_url('temp_pie.jpg'), style={'width':'100%'}), style = {'width': '20%'}, className = 'w3-row w3-col'),

            html.Div(
                dcc.Loading(id = "loading-icon", 
                    children=[
                        dcc.Graph(
                                id='trend-analysis', 
                                style={'height':'650px'})],
                    type="graph", 
                    style = {'margin': 'auto'}),
                    
                style = {'width': '60%'}, className = 'w3-row w3-col'),
                

            html.Div([
                dcc.Graph(
                    id = 'sex_hist', 
                    style = {'width': '400px',
                            'height': '375px',
                            'margin-top': '5%'}
                ) ,
                dcc.Graph(
                    id = 'race_hist',
                    style = {'width': '400px',
                            'height': '50%',
                            'margin-top': '5%'}
                )
            ], style = {'width': '20%'}, className = 'w3-row w3-col')
        ])
    ]
)

# Querying and Graphing Selected Data
@app.callback(
    Output('trend-analysis', 'figure'),
    Output('sex_hist', 'figure'),
    Output('race_hist', 'figure'),
    Output('insufficient-data', 'displayed'),
    Input('district_or_circuit_d', 'value'),
    Input('race_d', 'value'),
    Input('gender_d', 'value'),
    Input('charge_type_d', 'value'),
    Input('fips_code', 'value'),
    Input('disposition_type_d', 'value'))
def update_graph(district_or_circuit, race_name, sex_name, charge_type, fips_code, dispo_code):

    if district_or_circuit == None:
        district_or_circuit = 'circuit'

    if not bool(race_name):
        race_name = [*range(6)]

    if not bool(sex_name):
        sex_name = [*range(2)]
    
    if isinstance(fips_code, str):
        fips_code = [*fips_map.keys()]
    
    if not bool(charge_type):
        if district_or_circuit == 'circuit':
            charge_type = [*range(5)]
        else:
            charge_type = [*range(9)]

    if not bool(dispo_code):
        if district_or_circuit == 'circuit':
            dispo_code = [*range(12)]
        else:
            dispo_code = [*range(23)]

    query_str = '(' + ') & ('.join([f'Race in %s' % race_name,
                        f'Sex in %s' % sex_name,
                        f'ChargeType in %s' % charge_type,
                        f'DispositionCode in %s' % dispo_code,
                        f'FIPS in %s' % fips_code]) + ')'

    transformed_data = pd.concat((val for val in full_data[district_or_circuit].values()), 
                                keys = range(min(full_data[district_or_circuit]), max(full_data[district_or_circuit])+1)
                                ).reset_index(level=0).rename(columns = {'level_0':'YEAR'})

    transformed_data = transformed_data.query(query_str)
    transformed_data = transformed_data.groupby(['YEAR', 'Race', 'Sex'])['YEAR'].count().reset_index(name='count')

    transformed_data['Sex'] = transformed_data['Sex'].map(sex_map)
    transformed_data['Race'] = transformed_data['Race'].map(race_map)
    transformed_data['race_sex'] = transformed_data['Race'] + ' ' + transformed_data['Sex']

    fig = px.line(transformed_data, x='YEAR', y='count', color='race_sex', markers = True, labels={'race_sex':'Demographic',
                                                                                                    'YEAR': 'Year', 
                                                                                                    'count': 'Number of Arrests'})

    fig.update_xaxes(nticks = len(full_data[district_or_circuit]), showline=True, linewidth=2, linecolor='black', mirror=True)
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True)
    fig.update_layout(legend=dict(orientation= 'h', y=1.15, x = 0.5, xanchor = 'center', yanchor='top'))

    sex_fig = px.histogram(transformed_data, x = 'Sex', y='count', color = 'Sex')
    race_fig = px.histogram(transformed_data, x = 'Race', y='count', color = 'Race')

    if transformed_data.empty:
        return fig, sex_fig, race_fig, True

    return fig, sex_fig, race_fig, False

# Modifying Slider and Drop Down to be Dynamic
@app.callback(
    [Output('charge_type_d', 'options'),
    Output('disposition_type_d', 'options')],
    Input('district_or_circuit_d', 'value')
    )
def update_dynamic_dropdowns(district_or_circuit):

    if district_or_circuit == None:
        district_or_circuit = 'circuit'

    charge_options = [{'label': val, 'value': key} for key, val in sorted(charge_map[district_or_circuit].items(), key=lambda item: item[1])]
    disposition_options = [{'label': val, 'value': key} for key, val in sorted(dispo_map[district_or_circuit].items(), key=lambda item: item[1])]

    return charge_options, disposition_options


# %%
