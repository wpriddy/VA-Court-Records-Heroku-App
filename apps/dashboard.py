#%%

import plotly.express as px
import pandas as pd
import os


data = pd.read_csv(os.path.join('data', 'virginia_fips.csv'))

census_data = pd.read_pickle(r'..\ETL\data\census_clean.pickle')

transformed_data = data.groupby(['FIPS', 'Race', 'Sex'])['FIPS'].count().reset_index(name='count')

transformed_data = pd.merge(transformed_data, census_data[census_data.YEAR == 2003], how='left', left_on=['FIPS', 'Race', 'Sex'], right_on=['FIPS', 'Race', 'Gender']).drop(columns=['Gender', 'YEAR'])

transformed_data['Per Capita'] = transformed_data['count'] / transformed_data['population']

fig = px.sunburst(transformed_data, path=['Sex', 'Race'], values='population',
                  color='Per Capita')
fig.show()


# %%
# Add time series analysis (line graph)
# Add Bar Graph

#Look into using other visualization tactics with Dash