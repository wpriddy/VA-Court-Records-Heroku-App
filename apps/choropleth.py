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
                'color': colors['text']
            }),

    html.Div([

        html.Div([

            dcc.RadioItems(
                id='district_or_circuit',
                options = [{'label': 'Circuit', 'value': 'circuit'}, {'label': 'District', 'value': 'district'}],
                value = 'circuit',
                className = 'district_circuit_radio'
            ),

            html.Div(' a', style={'color':'white'}),

            dcc.RadioItems(
                id='adjust_per_capita',
                options = [{'label': 'Per Capita Arrests', 'value': 'True'}, {'label': 'Absolute Arrests', 'value': 'False'}],
                value = 'True',
                className = 'radio'
            ),

            html.Ul(children=[

            dcc.Dropdown(
                id='race',
                #Update to have own race list
                options=[{'label': val, 'value': key} for key, val in sorted(race_map.items(), key=lambda item: item[1])],
                value= 5,
                searchable=False,
                style={'background-color': '#DDD7D7', 'font-weight': 'bold'},
                className = 'race_dropdown'
            ),
            #This is a hack job, look to fix
            html.Div(' a', style={'color':'white'}),
            dcc.Dropdown(
                id='gender',
                #Update to have own sex list  
                options = [{'label': val, 'value': key} for key, val in sorted(sex_map.items(), key=lambda item: item[1])],
                value = 1,
                searchable=False,
                style={'background-color': '#DDD7D7', 'font-weight': 'bold'},
                className = 'gender_dropdown'
                ),
            html.Div(' a', style={'color':'white'}),
            dcc.Dropdown(
                id='charge_type',
                #Update to have own sex list  
                options = [{'label': val, 'value': key} for key, val in sorted(charge_map['circuit'].items(), key=lambda item: item[1])],
                value = 1,
                searchable=False,
                style={'background-color': '#DDD7D7', 'font-weight': 'bold'},
                className = 'charge_dropdown'
                ),
            html.Div(' a', style={'color':'white'}),
            dcc.Dropdown(
                id='disposition_type',
                #Update to have own sex list  
                options = [{'label': val, 'value': key} for key, val in sorted(dispo_map['circuit'].items(), key=lambda item: item[1])],
                value = 1,
                searchable=False,
                style={'background-color': '#DDD7D7', 'font-weight': 'bold'},
                className = 'dispo_dropdown'
                ),
            ]),

        ], style={'width': '300px', 'display': 'inline-block', 'text-align': 'center', 'margin': 'auto', 'float':'left'}),

        html.Div([

            dcc.Graph(
                id='interactive-graphic',
                style = {'border': '.5px solid black', 'width': '60%', 'margin': 'auto'},
                className = 'choropleth')
                ])

    ], style={'border': '3px solid #fff',
            'padding': '20px'}),

    html.Div(
        dcc.Slider(
        id='time-series',
        min = min(full_data['circuit']),
        max = max(full_data['circuit']),
        value = max(full_data['circuit']),
        marks = {str(k): {'label': str(k), 'style': {'font-weight': 'bold', 'font-size': '15px', 'color': '#000000'}} for k in full_data['circuit']},
        step=None,
        tooltip = {'placement':'top'},
        className = 'slider'
        )
)

])

# Querying and Graphing Selected Data
@app.callback(
    Output('interactive-graphic', 'figure'),
    Input('district_or_circuit', 'value'),
    Input('race', 'value'),
    Input('gender', 'value'),
    Input('time-series', 'value'),
    Input('adjust_per_capita', 'value'))
def update_graph(district_or_circuit: str, race_name: str, gender_name: str, year: int, per_capita: bool):

    transformed_data = full_data[district_or_circuit][year].groupby(['FIPS', 'Race', 'Sex'])['FIPS'].count().reset_index(name='count')

    # Create data frame with count=zero for every combination of FIPS, Area, Race, and Sex
    empty_data = pd.DataFrame(product(census_data.Sex.unique(), census_data.Race.unique(), census_data.FIPS.unique(), [0]), columns=['Sex', 'Race', 'FIPS', 'count'])

    # Concatenate and sum
    transformed_data = pd.concat([transformed_data, empty_data])
    transformed_data = transformed_data.groupby(['FIPS', 'Race', 'Sex']).sum().reset_index()

    transformed_data = transformed_data[(transformed_data.Race == race_name)&(transformed_data.Sex == gender_name)]

    # Final Data in Dictionary, use Year to Index data
    if per_capita == 'True':
        transformed_data = pd.merge(transformed_data, census_data[census_data.YEAR == year], how='left', left_on=['FIPS', 'Race', 'Sex'], right_on=['FIPS', 'Race', 'Sex']).drop(columns=['YEAR'])
        transformed_data['Per Capita Arrests'] = transformed_data['count'] / transformed_data['population']
        transformed_data['Area'] = transformed_data.FIPS.map(fips_map)

        #  Auto Adjust Legend Range to Fit Value
        color_range = (min(transformed_data['Per Capita Arrests']), max(transformed_data['Per Capita Arrests']))

        fig = px.choropleth(transformed_data, geojson=geo_map, locations='FIPS', color='Per Capita Arrests',
            color_continuous_scale='Viridis',
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
            color_continuous_scale='Viridis',
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
    [Output('time-series', 'min'),
    Output('time-series', 'max'),
    Output('time-series', 'marks')],
    Input('district_or_circuit', 'value')
    )
def update_dynamic_slider(district_or_circuit: str):

    min_val = min(full_data[district_or_circuit])
    max_val = max(full_data[district_or_circuit])
    marks_val = {str(k): {'label': str(k), 'style': {'font-weight': 'bold', 'font-size': '15px', 'color': '#000000'}} for k in full_data[district_or_circuit]}
    
    return min_val, max_val, marks_val 

@app.callback(
    [Output('charge_type', 'options'),
    Output('disposition_type', 'options')],
    Input('district_or_circuit', 'value')
    )
def update_dynamic_dropdowns(district_or_circuit):

    charge_options = [{'label': val, 'value': key} for key, val in sorted(charge_map[district_or_circuit].items(), key=lambda item: item[1])]
    disposition_options = [{'label': val, 'value': key} for key, val in sorted(dispo_map[district_or_circuit].items(), key=lambda item: item[1])]

    return charge_options, disposition_options



# %%
