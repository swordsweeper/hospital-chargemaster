#!/usr/bin/env python

import os
from glob import glob
import json
import pandas
import datetime

here = os.path.dirname(os.path.abspath(__file__))
folder = os.path.basename(here)
latest = '%s/latest' % here
year = datetime.datetime.today().year

output_data = os.path.join(here, 'data-latest.tsv')
output_year = os.path.join(here, 'data-%s.tsv' % year)

# Don't continue if we don't have latest folder
if not os.path.exists(latest):
    print('%s does not have parsed data.' % folder)
    sys.exit(0)

# Don't continue if we don't have results.json
results_json = os.path.join(latest, 'records.json')
if not os.path.exists(results_json):
    print('%s does not have results.json' % folder)
    sys.exit(1)

with open(results_json, 'r') as filey:
    results = json.loads(filey.read())

columns = ['charge_code', 
           'price', 
           'description', 
           'hospital_id', 
           'filename', 
           'charge_type']

df = pandas.DataFrame(columns=columns)

# First parse standard charges (doesn't have DRG header)
for result in results:
    filename = os.path.join(latest, result['filename'])
    if not os.path.exists(filename):
        print('%s is not found in latest folder.' % filename)
        continue

    if os.stat(filename).st_size == 0:
        print('%s is empty, skipping.' % filename)
        continue

    charge_type = 'standard'
    if "drg" in filename:
        charge_type = "drg"

    print("Parsing %s" % filename)

    if filename.endswith('xlsx'):

        if charge_type == "standard":

            content = pandas.read_excel(filename)

            # ['Charge Description Master', ' Charge ']
            # ['Drug Name', ' Charge ']
            # ['Supply Description Master', ' Charge ']     
        
            columns = content.columns.tolist()
            columns[0] = "Description"
            columns[1] = "Amount"
            content.columns = columns

            for row in content.iterrows():
                idx = df.shape[0] + 1

                if pandas.isnull(row[1]['Amount']):
                    continue

                code = None
                if "supply" in filename:
                    code = row[1]['Description'].split(' ')[0]
                entry = [code,                         # charge code
                         row[1]['Amount'],             # price
                         row[1]['Description'],        # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         charge_type]            
                df.loc[idx,:] = entry

        else:

            # 'James MS DRG', 
            # 'James Average Charge Per Case']
            content = pandas.read_excel(filename, skiprows=1)

            for row in content.iterrows():
                idx = df.shape[0] + 1

                if pandas.isnull(row[1]['James MS DRG']):
                    continue

                # Each row has two hospitals!
                code = row[1]['James MS DRG'].split('-')[0].strip()
                entry = [code,                         # charge code
                         row[1]['James Average Charge Per Case'],             # price
                         row[1]['James MS DRG'],        # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         charge_type]            
                df.loc[idx,:] = entry

                idx = df.shape[0] + 1

                # ['University Hospital MS DRG', 
                # 'UH Average Charge Per Case', 

                code = row[1]['University Hospital MS DRG'].split('-')[0].strip()
                entry = [code,                         # charge code
                         row[1]['UH Average Charge Per Case'],             # price
                         row[1]['University Hospital MS DRG'],        # description
                         result["hospital_id"],        # hospital_id
                         result['filename'],
                         charge_type]            
                df.loc[idx,:] = entry

# Remove empty rows
df = df.dropna(how='all')

# Save data!
print(df.shape)
df.to_csv(output_data, sep='\t', index=False)
df.to_csv(output_year, sep='\t', index=False)
