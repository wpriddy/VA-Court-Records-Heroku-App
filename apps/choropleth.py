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

    html.H1(children = 'Virginia Court Records Interactive Choropleth',
            style = {
                'textAlign': 'center',
                'color': colors['text'],
                'font-weight': 'bold',
                'margin-top': '20px'             
            }),

    html.Div([
            html.Div(
                dcc.Dropdown(
                    id='district_or_circuit',
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
                    id='time-series',
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
                    id='race',
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
                    id='gender',
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

    html.Div([
        html.Div(
            dcc.Dropdown(
                id='adjust_per_capita',
                options = [{'label': 'Per Capita Arrests', 'value': 'True'}, {'label': 'Absolute Arrests', 'value': 'False'}],
                value = 'True',
                searchable=False,
                style={'background-color': '#DDD7D7','width': '100%'},
                className = 'row',
                placeholder = 'Select a Metric'
            ), style =  {'width': '22%', 'display': 'inline-block'}),

        html.Div(' a'*2,  style={'color':'white'}),
        
        html.Div(
            dcc.Dropdown(
                id='charge_type',
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
                id='disposition_type',
                options = [{'label': val, 'value': key} for key, val in sorted(dispo_map['circuit'].items(), key=lambda item: item[1])],
                value = [0],
                searchable=False,
                multi=True,
                style={'background-color': '#DDD7D7','width': '100%'},
                className = 'row',
                placeholder = 'All Dispositions'
            ), style =  {'width': '22%', 'display': 'inline-block'}),
            
            html.H3('Data Table', style={'margin': 'auto'}, className='row')
            ], style={'display':'flex', 'margin':'1.5em'}
        ),

        html.Div([

            dcc.Graph(
                id='interactive-graphic',
                style = {'border': '.5px solid black', 'margin-left': '28px'},
                className = 'w3-row w3-twothird'),

                html.Div([
                    
                    dash_table.DataTable(
                                    id = 'dataTable',
                                    style_table = {'overflowY': 'scroll',
                                                    'overflowX': 'scroll', 
                                                    'margin-left': '4%', 
                                                    'width': '117%', 
                                                    'maxHeight': '453px',
                                                    'border': '1px solid black'},
                                    style_data = {'height': 'auto'},
                                    style_data_conditional=[
                                        {
                                            'if': {'row_index': 'odd'},
                                            'backgroundColor': 'rgb(220, 220, 220)',
                                        }
                                    ],
                                    style_header={
                                        'backgroundColor': 'rgb(210, 210, 210)',
                                        'color': 'black',
                                        'fontWeight': 'bold'
                                    },
                                    style_cell_conditional=[
                                        {
                                            'if': {'column_id': c},
                                            'textAlign': 'left'
                                        } for c in ['Area']
                                    ],
                                    sort_action = 'native'
                                )
                        ], className = 'w3-row w3-quarter w3-border-black')
                ])
        ] 
)

# Querying and Graphing Selected Data
@app.callback(
    Output('interactive-graphic', 'figure'),
    Output('dataTable', 'data'),
    Output('dataTable', 'columns'),
    Input('district_or_circuit', 'value'),
    Input('race', 'value'),
    Input('gender', 'value'),
    Input('time-series', 'value'),
    Input('adjust_per_capita', 'value'),
    Input('charge_type', 'value'),
    Input('disposition_type', 'value'))
def update_graph(district_or_circuit, race_name, sex_name, year, per_capita, charge_type, dispo_code):

    if district_or_circuit == None:
        district_or_circuit = 'circuit'

    if per_capita == None:
        per_capita = 'True'

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

    transformed_data = pd.concat(val for key, val in full_data[district_or_circuit].items() if int(key) in year).groupby(['FIPS', 'Race', 'Sex', 'ChargeType', 'DispositionCode'])['FIPS'].count().reset_index(name='count')

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

    query_str = '(' + ') & ('.join([f'Race in %s' % race_name,
                        f'Sex in %s' % sex_name,
                        f'ChargeType in %s' % charge_type,
                        f'DispositionCode in %s' % dispo_code]) + ')'

    if len(year) < 2:
        transformed_data = transformed_data.query(query_str).groupby(['FIPS'])['count'].sum().reset_index()
    else:
        # TODO Potentally buggy due to Means and the Zero dataframe
        transformed_data = transformed_data.query(query_str).groupby(['FIPS'])['count'].mean().astype(int).reset_index()

    # Final Data in Dictionary, use Year to Index data
    if per_capita == 'True':

        census_query_str = '(' + ') & ('.join([f'Race in %s' % race_name,
                                               f'Sex in %s' % sex_name, 
                                               f'YEAR in %s' % year]) + ')'
        
        census = census_data.query(census_query_str)
        
        if len(year) < 2:
            census = census.groupby(['FIPS'])['population'].sum().reset_index()
        else:
            census = census.groupby(['FIPS'])['population'].mean().astype(int).reset_index()

        transformed_data = pd.merge(transformed_data, census, how='left', left_on=['FIPS'], right_on=['FIPS'])
        transformed_data['Per Capita Arrests'] = transformed_data['count'] / transformed_data['population']
        transformed_data['Area'] = transformed_data.FIPS.map(fips_map)
        
        #  Auto Adjust Legend Range to Fit Value
        color_range = (min(transformed_data['Per Capita Arrests']), max(transformed_data['Per Capita Arrests']))

        fig = px.choropleth(transformed_data, geojson=geo_map, locations='FIPS', color='Per Capita Arrests',
            color_continuous_scale='ylorbr',
            range_color = color_range,
            scope='usa',   # Update to Only show virginia
            labels={'count': 'Arrests'},
            hover_name = 'Area',
            hover_data = ['population', 'count']
        )
        
        data = transformed_data[['Area', 'Per Capita Arrests']].sort_values(['Per Capita Arrests'], ascending=False).to_dict('records')
        columns = [{"name": i, "id": i} for i in ['Area', 'Per Capita Arrests']]
    else:
        #  Auto Adjust Legend Range to Fit Value
        transformed_data['Area'] = transformed_data.FIPS.map(fips_map)
        color_range = (min(transformed_data['count']), max(transformed_data['count']))

        fig = px.choropleth(transformed_data, geojson=geo_map, locations='FIPS', color='count',
            color_continuous_scale='ylorbr',
            range_color = color_range,
            scope='usa',   # Update to Only show virginia
            labels={'count': 'arrests'},
            hover_name = 'Area'
        )
        # TODO There are null values in District when mapped to fips_map
        data = transformed_data[['Area', 'count']].sort_values(['count'], ascending=False).to_dict('records')
        columns = [{"name": i, "id": i} for i in transformed_data[['Area', 'count']].columns]

    fig.update_geos(fitbounds="locations")
    fig.update_layout(margin={'r':0,'t':0,'l':0,'b':0})

    return fig, data, columns

# Modifying Slider and Drop Down to be Dynamic
@app.callback(
    [Output('charge_type', 'options'),
    Output('disposition_type', 'options'),
    Output('time-series', 'options')], 
    Output('time-series', 'value'),
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
