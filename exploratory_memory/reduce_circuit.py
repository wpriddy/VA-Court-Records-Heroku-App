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

full_data = {'circuit': {}, 'district': {}}


def read_bucket(bucket: str, key, dataset):

    full_data[dataset][key] = pickle.loads(s3_client.get_object(Bucket = bucket, Key=str(key)+'.pickle')['Body'].read())

with ThreadPoolExecutor() as executor:

    futures = {
        executor.submit(read_bucket, 'va-courts-circuit', year, 'circuit'): year for year in circuit_keys
    }



# %%
from sys import getsizeof as size

circuit_small = {}

original_sizes = {year: size(full_data['circuit'][year]) for year in full_data['circuit']}

for year in full_data['circuit']:

    data = full_data['circuit'][year].copy()

    data = data[~data['DispositionCode'].isnull()]

    sex_map = {'Male': 0, 
              'Female': 1}

    race_map = {'White': 0,
                'Hispanic': 1,
                'Black':2,
                'Unknown':3,
                'Asian': 4,
                'American Indian':5}

    charge_map = {'Misdemeanor':0,
                'Felony': 1,
                'Other (Animal Violations, Bond Appeals)':2,
                'Infraction':3, 
                'Civil':4}

    # Need to Drop Nan in DispositionCode
    disposition_map = {'Dismissed':0,
                    'Not Guilty/Acquitted':1,
                    'Guilty':2,
                    'Nolle Prosequi':3,
                    'Appeal Withdrawn':4,
                    'Sentence/Probation Revoked':5,
                    'Resolved':6,
                    'No Indictment Presented': 7,
                    'Not True Bill':8,
                    'Remanded': 9,
                    'Not Guilty By Reason Of Insanity':10,
                    'Mistrial':11}

    data.Sex = data.Sex.map(sex_map)
    data.Race = data.Race.map(race_map)
    data.ChargeType = data.ChargeType.map(charge_map)
    data.DispositionCode = data.DispositionCode.map(disposition_map)
    data = data.drop(columns=['Class', 'Area'])
    circuit_small[year] = data.astype('int32')

reduced_size = {year: size(circuit_small[year]) for year in circuit_small}

# %%
for year in original_sizes:
    print(year, ': ', round(reduced_size[year]/original_sizes[year], 2), '% -', round(reduced_size[year]/10**9, 4), 'GB')

print('Total:', round(sum([val for key,val in reduced_size.items()]) / 10**9, 2), 'GB')
# %%
for year in circuit_small:

    circuit_small[year].to_pickle(r'.\circuit\{}.pickle'.format(year))
# %%
