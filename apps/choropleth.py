#%%
from dash import dcc, html
from dash.dependencies import Input, Output
from itertools import product
import sys
sys.path.insert(0, r'..')
from app import app
import json
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

    html.H1(children = 'Virginia Court Records Interactive Choropleth',
            style = {
                'textAlign': 'center',
                'color': colors['text'],
                'font-weight': 'bold'               
            }),

    html.Div([
            dcc.Dropdown(
                id='district_or_circuit',
                options = [{'label': 'Circuit', 'value': 'circuit'}, {'label': 'District', 'value': 'district'}],
                value = 'circuit',
                searchable=False, 
                style={'background-color': '#DDD7D7','width': '275px'},
                className = 'row w3-row w3-third'
            ),

            html.Div(' a'*2,  style={'color':'white'}),

            dcc.Dropdown(
                id='time-series',
                options = [{'label': str(k), 'value': k} for k in full_data['circuit']],
                value = max(full_data['circuit']),
                searchable=False,
                style={'background-color': '#DDD7D7','width': '275px'},
                className = 'row w3-row w3-third'
                ),

            html.Div(' a'*2,  style={'color':'white'}),

            dcc.Dropdown(
                id='race',
                options=[{'label': val, 'value': key} for key, val in sorted(race_map.items(), key=lambda item: item[1])],
                value= 5,
                searchable=False,
                style={'background-color': '#DDD7D7','width': '275px'},
                className = 'row w3-row w3-third'
            ),
            
            html.Div(' a'*2,  style={'color':'white'}),

            dcc.Dropdown(
                id='gender',
                options = [{'label': val, 'value': key} for key, val in sorted(sex_map.items(), key=lambda item: item[1])],
                value = 1,
                searchable=False,
                style={'background-color': '#DDD7D7','width': '275px'},
                className = 'row w3-row w3-third'
                ),
            ], style={'display':'flex', 'margin':'1.5em'}
        ),

        html.Div([

            dcc.Dropdown(
                id='adjust_per_capita',
                options = [{'label': 'Per Capita Arrests', 'value': 'True'}, {'label': 'Absolute Arrests', 'value': 'False'}],
                value = 'True',
                searchable=False,
                style={'background-color': '#DDD7D7','width': '375px'},
                className = 'row w3-row w3-quarter'
            ),

            html.Div(' a'*2,  style={'color':'white'}),

            dcc.Dropdown(
                id='charge_type',
                options = [{'label': val, 'value': key} for key, val in sorted(charge_map['circuit'].items(), key=lambda item: item[1])],
                value = 0,
                searchable=False,
                style={'background-color': '#DDD7D7','width': '375px'},
                className = 'row w3-row w3-quarter'
                ),
            
            html.Div(' a'*2,  style={'color':'white'}),

            dcc.Dropdown(
                id='disposition_type',
                options = [{'label': val, 'value': key} for key, val in sorted(dispo_map['circuit'].items(), key=lambda item: item[1])],
                value = 0,
                searchable=False,
                style={'background-color': '#DDD7D7','width': '375px'},
                className = 'row w3-row w3-quarter'
                ),
            
            html.H3('Summary Statistics', style={'margin-left': '140px'}, className='row')
            ], style={'display':'flex', 'margin':'1.5em'}
        ),

        html.Div([

            dcc.Graph(
                id='interactive-graphic',
                style = {'border': '.5px solid black', 'margin-left': '28px'},
                className = 'w3 row w3-twothird'),

                html.Div([
                    html.Img(src = app.get_asset_url('temp_graph.png'), style={'height': '220px', 'margin-left':'150px', 'margin-right': '28px'}), 
                    
                    html.Img(src = app.get_asset_url('temp_pie.jpg'), style={'height':'220px', 'margin-left':'150px', 'margin-right': '28px'})
                    
                    ], )
                ]),
    ]
)

# Querying and Graphing Selected Data
@app.callback(
    Output('interactive-graphic', 'figure'),
    Input('district_or_circuit', 'value'),
    Input('race', 'value'),
    Input('gender', 'value'),
    Input('time-series', 'value'),
    Input('adjust_per_capita', 'value'),
    Input('charge_type', 'value'),
    Input('disposition_type', 'value'))
def update_graph(district_or_circuit, race_name, gender_name, year, per_capita, charge_type, dispo_code):

    transformed_data = full_data[district_or_circuit][year].groupby(['FIPS', 'Race', 'Sex', 'ChargeType', 'DispositionCode'])['FIPS'].count().reset_index(name='count')

    # Create data frame with count=zero for every combination of FIPS, Area, Race, and Sex
    empty_data = pd.DataFrame(product(
                                census_data.Sex.unique(), 
                                census_data.Race.unique(),
                                census_data.FIPS.unique(),
                                charge_map[district_or_circuit].keys(),
                                dispo_map[district_or_circuit].keys(),
                                [0]), columns=['Sex', 'Race', 'FIPS', 'ChargeType', 'DispositionCode', 'count'])

    # Concatenate and sum
    transformed_data = pd.concat([transformed_data, empty_data])
    transformed_data = transformed_data.groupby(['FIPS', 'Race', 'Sex', 'ChargeType', 'DispositionCode']).sum().reset_index()

    transformed_data.query(f'Race == {race_name} & Sex == {gender_name} & ChargeType == {charge_type} & DispositionCode == {dispo_code}'
                        , inplace=True)

    # Final Data in Dictionary, use Year to Index data
    if per_capita == 'True':
        transformed_data = pd.merge(transformed_data, census_data[census_data.YEAR == year], how='left', left_on=['FIPS', 'Race', 'Sex'], right_on=['FIPS', 'Race', 'Sex']).drop(columns=['YEAR'])
        transformed_data['Per Capita Arrests'] = transformed_data['count'] / transformed_data['population']
        transformed_data['Area'] = transformed_data.FIPS.map(fips_map)

        #  Auto Adjust Legend Range to Fit Value
        color_range = (min(transformed_data['Per Capita Arrests']), max(transformed_data['Per Capita Arrests']))

        fig = px.choropleth(transformed_data, geojson=geo_map, locations='FIPS', color='Per Capita Arrests',
            color_continuous_scale='ylorbr',
            range_color = color_range,
            scope='usa',   # Update to Only show virginia
            labels={race_name: race_name ,'count': 'arrests'},
            hover_name = 'Area',
            hover_data = ['population', 'count']
        )
    else:
        #  Auto Adjust Legend Range to Fit Value
        transformed_data['Area'] = transformed_data.FIPS.map(fips_map)
        color_range = (min(transformed_data['count']), max(transformed_data['count']))

        fig = px.choropleth(transformed_data, geojson=geo_map, locations='FIPS', color='count',
            color_continuous_scale='ylorbr',
            range_color = color_range,
            scope='usa',   # Update to Only show virginia
            labels={race_name: race_name, 'count': 'Arrests'},
            hover_name = 'Area'
        )
    fig.update_geos(fitbounds="locations")
    fig.update_layout(margin={'r':0,'t':0,'l':0,'b':0})

    return fig

# Modifying Slider and Drop Down to be Dynamic
@app.callback(
    [Output('charge_type', 'options'),
    Output('disposition_type', 'options'),
    Output('time-series', 'options')], 
    Output('time-series', 'value'),
    Input('district_or_circuit', 'value')
    )
def update_dynamic_dropdowns(district_or_circuit):

    charge_options = [{'label': val, 'value': key} for key, val in sorted(charge_map[district_or_circuit].items(), key=lambda item: item[1])]
    disposition_options = [{'label': val, 'value': key} for key, val in sorted(dispo_map[district_or_circuit].items(), key=lambda item: item[1])]
    year_options = [{'label': str(k), 'value': k} for k in full_data[district_or_circuit]]
    year_value = max(full_data[district_or_circuit])

    return charge_options, disposition_options, year_options, year_value



# %%
