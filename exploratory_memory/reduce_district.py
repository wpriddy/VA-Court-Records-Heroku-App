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

circuit_keys = range(2007, 2021)

full_data = {'circuit': {}, 'district': {}}


def read_bucket(key, dataset):

    full_data[dataset][key] = pickle.loads(s3_client.get_object(Bucket = 'va-courts', Key='district/' +str(key)+'.pickle')['Body'].read())

with ThreadPoolExecutor() as executor:

    futures = {
        executor.submit(read_bucket, year, 'district'): year for year in circuit_keys
    }

# %%
clean_data = {}

# Clean Up District
for year in full_data['district']:

    data = full_data['district'][year]

    data = data[~data['Gender'].isnull()]

    data = data[~data['Race'].isnull()]

    data = data[~data['CaseType'].isnull()]

    data = data[~data['FinalDisposition'].isnull()]

    data['fips'] = data['fips'].apply(lambda x: int('51'+str(x).zfill(3)))

    data = data[['Gender', 'Race', 'CaseType','FinalDisposition', 'fips']]

    clean_data[year] = data
#%%

#%%
from sys import getsizeof as size

district_small = {}

original_sizes = {year: size(clean_data[year]) for year in clean_data}

for year in clean_data:

    data = clean_data[year].copy()

    sex_map = {'Male': 0, 
              'Female': 1}

    race_map = {'White': 0,
                'Hispanic': 1,
                'Black':2,
                'Unknown':3,
                'Asian': 4,
                'American Indian':5}

    case_map = {'Misdemeanor':0,
                'Infraction':1,
                'Felony':2,
                'Capias':3,
                'Other': 4,
                "Restricted Operator's License": 5,
                "Restricted Operator's License For Fine and Costs Only":5,
                'Motion [18.2-271.1(E)]': 5, # Make 5 to "Restricted Operators License"
                'Show Cause':6,
                'Civil Violation':7,
                'Non Case':8}

    disposition_map = {'Fugitive File':0,
                     'Nolle Prosequi':1,
                      'Guilty':3,
                       'Dismissed':4,
                        'Other':5,
                    'Not Guilty':6,
                    'Guilty In Absentia':7,
                    'Certified To Grand Jury':8,
                    'Extradition Waived':9,
                    'Transferred To Another Jurisdiction/Court':10,
                    'Prepaid':11,
                    'Complied With Law':12,
                    'Defendant Not Found':13,
                    'Sentence/Probation Revoked':14,
                    'Denied': 15,
                     'Dismissed/Other':16,
                     'Not Guilty/Insanity':17, 
                     'Bond Forfeited':18, 
                     'Certified Misdemeanor':19,
                      'Extradition Ordered':20, 
                      'Granted':21, 
                      'Adjudicated Habitual Offender':22}



    data.Gender = data.Gender.map(sex_map).astype('int8')
    data.Race = data.Race.map(race_map).astype('int8')
    data.CaseType = data.CaseType.map(case_map).astype('int8')
    data.FinalDisposition = data.FinalDisposition.map(disposition_map).astype('int8')
    data.fips = data.fips.astype('int32')
    district_small[year] = data
    

reduced_size = {year: size(district_small[year]) for year in district_small}

# %%
for year in original_sizes:
    print(year, ': ', round(reduced_size[year]/original_sizes[year], 2), '% -', round(reduced_size[year]/10**9, 4), 'GB')

print('Total:', round(sum([val for key,val in reduced_size.items()]) / 10**9, 2), 'GB')
# %%
for year in district_small:

    district_small[year].to_pickle(r'.\district\{}.pickle'.format(year))
# %%
