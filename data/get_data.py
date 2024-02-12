#%%
import pandas as pd
import boto3
import json
import pickle
import os


tempermental_medium = '.'

tokens = {'access key ID': 'SECRET',
        'access key': 'SECRET'
        }


session = boto3.Session()

s3_client = session.client(
    's3',
    aws_access_key_id = tokens['access key ID'],
    aws_secret_access_key = tokens['access key'],
    region_name = 'us-east-1'
)


full_data = {'circuit': {year: pd.read_pickle(os.path.join(tempermental_medium, 'data', 'files', 'circuit', str(year) + '.pickle')) for year in range(2000, 2021)},
             'district': {year: pd.read_pickle(os.path.join(tempermental_medium, 'data', 'files', 'district', str(year) + '.pickle')) for year in range(2009, 2021)}
             }

race_map = pd.read_pickle(os.path.join(tempermental_medium, 'data', 'files' , 'race_map.pickle'))
sex_map = pd.read_pickle(os.path.join(tempermental_medium, 'data', 'files' , 'sex_map.pickle'))

charge_map = {'circuit': pd.read_pickle(os.path.join(tempermental_medium, 'data', 'files' , 'circuit_charge_map.pickle')),
              'district': pd.read_pickle(os.path.join(tempermental_medium, 'data', 'files' , 'district_casetype_map.pickle'))}

dispo_map = {'circuit': pd.read_pickle(os.path.join(tempermental_medium, 'data', 'files' , 'circuit_disposition_map.pickle')),
             'district': pd.read_pickle(os.path.join(tempermental_medium, 'data', 'files' , 'district_disposition_map.pickle'))}

census_data = pd.read_pickle(os.path.join(tempermental_medium, 'data', 'files' , 'census_data.pickle'))

geo_map = json.loads(s3_client.get_object(Bucket = 'va-courts-other', Key='geo_main.json')['Body'].read())
# %%


