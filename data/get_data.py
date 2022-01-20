#%%
import pandas as pd
import boto3
import json
import pickle
import os

tokens = {'access key ID': 'AKIA6GKIQREKFAYKTX6N',
        'access key': 'aNBWg/pptHHydedMFeDvZFl4X5Yz9YpwfGhpQcFV'
        }


session = boto3.Session()

s3_client = session.client(
    's3',
    aws_access_key_id = tokens['access key ID'],
    aws_secret_access_key = tokens['access key'],
    region_name = 'us-east-1'
)


full_data = {'circuit': {year: pd.read_pickle(os.path.abspath(os.path.join('data', 'files', 'circuit', str(year) + '.pickle'))) for year in range(2000, 2021)},
             'district': {year: pd.read_pickle(os.path.abspath(os.path.join('data', 'files', 'district', str(year) + '.pickle'))) for year in range(2007, 2021)}
             }

census_data = pickle.loads(s3_client.get_object(Bucket = 'va-courts-other', Key='census_clean.pickle')['Body'].read())

geo_map = json.loads(s3_client.get_object(Bucket = 'va-courts-other', Key='geo_main.json')['Body'].read())
# %%


