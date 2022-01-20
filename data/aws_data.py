#%%
import pandas as pd
import boto3
import json
import pickle
from concurrent.futures import ThreadPoolExecutor
import time

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

circuit_keys = range(2000, 2021)
district_keys = range(2007, 2021)

full_data = {'circuit': {}, 'district': {}}


def read_bucket(bucket: str, key, dataset):

    full_data[dataset][key] = pickle.loads(s3_client.get_object(Bucket = bucket, Key=str(key)+'.pickle')['Body'].read())

with ThreadPoolExecutor() as executor:

    futures = {
        executor.submit(read_bucket, 'va-courts-circuit', year, 'circuit'): year for year in circuit_keys
    }

    # futures2 = {
    #     executor.submit(read_bucket, 'va-courts-district', year, 'district'): year for year in district_keys
    # }

census_data = pickle.loads(s3_client.get_object(Bucket = 'va-courts-other', Key='census_clean.pickle')['Body'].read())

geo_map = json.loads(s3_client.get_object(Bucket = 'va-courts-other', Key='geo_main.json')['Body'].read())
# %%


