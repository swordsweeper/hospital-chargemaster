#!/usr/bin/env python

import os
import requests
import json
import datetime
import shutil
from bs4 import BeautifulSoup

here = os.path.dirname(os.path.abspath(__file__))
hospital_id = os.path.basename(here)

root_url = 'https://healthcare.ascension.org'
url = f'{root_url}/price-transparency/price-transparency-files'
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
}

today = datetime.datetime.today().strftime('%Y-%m-%d')
outdir = os.path.join(here, today)
if not os.path.exists(outdir):
    os.mkdir(outdir)

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, 'lxml')

# Each folder will have a list of records
records = []

index = 0
for entry in soup.find_all('a', href=True):
    download_url = entry['href']
    #print(f'found url: {download_url}')
    if '.xlsx' in download_url:  
        index += 1
        if(index > 5):
            pass#break

        filename =  os.path.basename(download_url.split('?')[0])  

        entry_name = entry.text
        entry_uri = entry_name.strip().lower().replace(' ','-')
        # We want to get the original file, not write a new one
        output_file = os.path.join(outdir, filename)
        os.system('wget -O "%s" "%s"' % (output_file, f"{root_url}{download_url}"))

        record = { 'hospital_id': hospital_id,
                   'filename': filename,
                   'date': today,
                   'uri': entry_uri,
                   'name': entry_name,
                   'url': f"{root_url}{download_url}"
        }

        records.append(record)

print("all finished parsing.")

# Keep json record of all files included
records_file = os.path.join(outdir, 'records.json')
with open(records_file, 'w') as filey:
    filey.write(json.dumps(records, indent=4))

# This folder is also latest.
latest = os.path.join(here, 'latest')
if os.path.exists(latest):
    shutil.rmtree(latest)

shutil.copytree(outdir, latest)
