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

    html.H1(children = 'Virginia Court Records Interactive Dashboard',
            style = {
                'textAlign': 'center',
                'color': colors['text'],
                'font-weight': 'bold'               
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
                ), style={'width': '16.2%', 'display': 'inline-block'}),

            html.Div(' a'*2,  style={'color':'white'}),

            html.Div(
                dcc.Dropdown(
                    id='time-series_d',
                    options = [{'label': str(k), 'value': k} for k in sorted(full_data['circuit'], reverse=True)],
                    value = [max(full_data['circuit'])],
                    searchable=False,
                    multi=True,
                    style={'background-color': '#DDD7D7','width': '100%'},
                    className = 'row',
                    placeholder = 'All Years'
                ), style = {'width': '16.2%', 'display': 'inline-block'}),

            html.Div(' a'*2,  style={'color':'white'}),

            html.Div(
                dcc.Dropdown(
                    id='race_d',
                    options=[{'label': val, 'value': key} for key, val in sorted(race_map.items(), key=lambda item: item[1])],
                    value= [5],
                    searchable=False,
                    multi=True,
                    style={'background-color': '#DDD7D7','width': '100%'},
                    className = 'row',
                    placeholder = 'All Races'
                ), style = {'width': '16.2%', 'display': 'inline-block'}),
            
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
                ), style = {'width': '16.2%', 'display': 'inline-block'})

        ], style={'display':'flex', 'margin':'1.5em'}
    ),

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
            ), style =  {'width': '22%', 'display': 'inline-block'}),
            
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
            ), style =  {'width': '22%', 'display': 'inline-block'}),

        html.Div([

            dcc.Graph(id='trend-analysis')
        ])
    ]
)

# Querying and Graphing Selected Data
@app.callback(
    Output('trend-analysis', 'figure'),
    Input('district_or_circuit_d', 'value'),
    Input('race_d', 'value'),
    Input('gender_d', 'value'),
    Input('time-series_d', 'value'),
    Input('charge_type_d', 'value'),
    Input('disposition_type_d', 'value'))
def update_graph(district_or_circuit, race_name, sex_name, year, charge_type, dispo_code):

    if district_or_circuit == None:
        district_or_circuit = 'circuit'

    if not bool(race_name):
        race_name = [*range(6)]

    if not bool(sex_name):
        sex_name = [*range(2)]

    if not bool(year):
        if district_or_circuit == 'circuit':
            year = [*range(min(full_data['circuit']), max(full_data['circuit']) + 1)]
        else:
            year = [*range(min(full_data['district']), max(full_data['district']) + 1)]
    
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

    transformed_data = pd.concat((val for key, val in full_data[district_or_circuit].items() if int(key) in year), keys = year).reset_index(level=0).rename(columns = {'level_0':'YEAR'})
    transformed_data = transformed_data.groupby(['YEAR', 'Race', 'Sex', 'ChargeType', 'DispositionCode'])['YEAR'].count().reset_index(name='count')
    
    fig = px.line(transformed_data, x='YEAR', y='count', color='count', markers = True)

    return fig

# Modifying Slider and Drop Down to be Dynamic
@app.callback(
    [Output('charge_type_d', 'options'),
    Output('disposition_type_d', 'options'),
    Output('time-series_d', 'options')], 
    Output('time-series_d', 'value'),
    Input('district_or_circuit', 'value')
    )
def update_dynamic_dropdowns(district_or_circuit):

    if district_or_circuit == None:
        district_or_circuit = 'circuit'

    charge_options = [{'label': val, 'value': key} for key, val in sorted(charge_map[district_or_circuit].items(), key=lambda item: item[1])]
    disposition_options = [{'label': val, 'value': key} for key, val in sorted(dispo_map[district_or_circuit].items(), key=lambda item: item[1])]
    year_options = [{'label': str(k), 'value': k} for k in sorted(full_data[district_or_circuit], reverse=True)]
    year_value = [max(full_data[district_or_circuit])]

    return charge_options, disposition_options, year_options, year_value



# %%
