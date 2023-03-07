#!/usr/bin/env python

import os
from glob import glob
import json
import pandas
import datetime

skip_rows = 1
#file = '630909073_saint-vincents-blount_standardcharges.xlsx'
column_map = {
    'proc_code': 2,#"Code", 
    'code_type': 1,#"Code_Type",
    'description': 3,#"Description",
    'rev_code': 4,#"UB_Revenue_Code",
    'gross_amount': 6,#'Gross_Charge',
    'cash_amount': 7,#'Cash_Charge',
    'negotiated_min': 8,#'Min_Negotiated_Rate',
    'negotiated_max': 9,#'Max_Negotiated_Rate'
}

here = os.path.dirname(os.path.abspath(__file__))
folder = os.path.basename(here)
latest = '%s/latest' % here
year = datetime.datetime.today().year

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

all_columns = ['proc_code', 
           'code_type', 
           'description', 
           'rev_code', 
           'gross_amount',
           'cash_amount',
           'negotiated_min',
           'negotiated_max',
           'cms_amount']   

columns = []

# First parse standard charges (doesn't have DRG header)
for result in results:
    filename = os.path.join(latest, result['filename'])
    output_data = os.path.join(here, 'json', f"{result['uri']}-data-latest.json")

    if not os.path.exists(os.path.join(here, 'json')):
        os.mkdir(os.path.join(here, 'json'))

    if not os.path.exists(filename):
        print('%s is not found in latest folder.' % filename)
        sys.exit(1)

    if os.stat(filename).st_size == 0:
        print('%s is empty, skipping.' % filename)
        sys.exit(1)

    print("Parsing %s" % filename)
    for col in all_columns:
        try:
            column_map[f"{col}"]
            columns.append(col)
        except Exception as e:
            print(f'no column is defined for {e}')

    df = pandas.DataFrame(columns=columns)
    if filename.endswith('xlsx'):
        content = pandas.read_excel(filename, skiprows=skip_rows, sheet_name="Standard Charges")

        for row in content.values:
            idx = df.shape[0] + 1

            entry = []
            for col in columns: 
                source_column = column_map[f"{col}"]
                entry.append(row[source_column])     
            df.loc[idx,:] = entry

    # Remove empty rows
    df = df.dropna(how='all')

    # Save data!
    print(df.shape)
    df.to_json(output_data, orient='table', index=False)
    df.to_csv(output_year, sep='\t', index=False)
