#%%
from dash import dcc, html
from dash.dependencies import Input, Output
from concurrent.futures import ThreadPoolExecutor
from itertools import product
from app import app
import json
import plotly.express as px
import pandas as pd
import pathlib
from data.aws_data import circuit, census_data, geo_map

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()

colors = {
    'background': '#111111',
    'text': '#2C2C2C'
}

data = circuit

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
                id='adjust_per_capita',
                options = [{'label': 'Per Capita Arrests', 'value': 'True'}, {'label': 'Absolute Arrests', 'value': 'False'}],
                value = 'True',
                className = 'radio'
            ),

            html.Ul(children=[

            dcc.Dropdown(
                id='race',
                #Update to have own race list
                options=sorted([{'label': i, 'value': i} for i in data[2000].Race.unique() if i == i], key=lambda x: x['label']),
                value= 'American Indian',
                searchable=False,
                style={'background-color': '#DDD7D7', 'font-weight': 'bold'},
                className = 'race_dropdown'
            ),
            #This is a hack job, look to fix
            html.Div(' a', style={'color':'white'}),
            dcc.Dropdown(
                id='gender',
                #Update to have own sex list
                options = sorted([{'label': i, 'value': i} for i in data[2000].Sex.unique() if i == i], key=lambda x: x['label']),
                value = 'Female',
                searchable=False,
                style={'background-color': '#DDD7D7', 'font-weight': 'bold'},
                className = 'gender_dropdown'
                )
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
        min = min(data),
        max = max(data),
        value = max(data),
        marks = {str(k): {'label': str(k), 'style': {'font-weight': 'bold', 'font-size': '15px', 'color': '#000000'}} for k in data},
        step=None,
        tooltip = {'placement':'top'},
        className = 'slider'
        )
    )

])

@app.callback(
    Output('interactive-graphic', 'figure'),
    Input('race', 'value'),
    Input('gender', 'value'),
    Input('time-series', 'value'),
    Input('adjust_per_capita', 'value'))
def update_graph(race_name: str, gender_name: str, year: int, per_capita: bool):

    transformed_data = data[year].groupby(['FIPS', 'Area', 'Race', 'Sex'])['FIPS'].count().reset_index(name='count')

    # Create data frame with count=zero for every combination of FIPS, Area, Race, and Sex
    empty_data = pd.DataFrame(product(census_data.Gender.unique(), census_data.Race.unique(), census_data.FIPS.unique(), [0]), columns=['Sex', 'Race', 'FIPS', 'count'])
    empty_data['Area'] = empty_data.FIPS.map(fips_map)

    # Concatenate and sum
    transformed_data = pd.concat([transformed_data, empty_data])
    transformed_data = transformed_data.groupby(['FIPS', 'Area', 'Race', 'Sex']).sum().reset_index()

    transformed_data = transformed_data[(transformed_data.Race == race_name)&(transformed_data.Sex == gender_name)]

    #Final Data in Dictionary, use Year to Index data
    if per_capita == 'True':
        transformed_data = pd.merge(transformed_data, census_data[census_data.YEAR == year], how='left', left_on=['FIPS', 'Race', 'Sex'], right_on=['FIPS', 'Race', 'Gender']).drop(columns=['Gender', 'YEAR'])
        transformed_data['Per Capita Arrests'] = transformed_data['count'] / transformed_data['population']
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
# %%
