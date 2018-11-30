'''
This is the same code from the iPython Notebook version of 'scraping_stl_crimedata.'

Must install prereqs first:

requests
BeautifulSoup

'''

import requests
from bs4 import BeautifulSoup
import re
import os
import time

# URL
url = 'http://www.slmpd.org/CrimeReport.aspx'

# Path to save location
path = 'raw_data/'

def get_filename(headers):
    """Parses out the filename from a response header."""
    return headers['content-disposition'].split('=')[1]

payload = {}

# The first page request is a get to the url.
r = requests.get(url)
soup = BeautifulSoup(r.content, "html.parser")

# Get the three hidden parameter values.
payload_raw = soup.find_all('input')
payload = {x['name']:x['value'] for x in payload_raw}

# List to hold eventtargets.
datasets_eventtargets_raw = []

# Get the data for this page and store it.
links = soup.find_all(href=re.compile("javascript:__doPostBack\('.*D',''\)"))
datasets_eventtargets_raw.append((1, dict(payload), links))
    
# Set EventTarget for page requesting.
payload['__EVENTTARGET'] = 'GridView1'

# Loop through all pages.
for i in range(2,7):
    # Set the eventargument value in the payload.
    payload['__EVENTARGUMENT'] = 'Page$' + str(i)
    
    # Request the page, make a soup object, get all relevant tags.
    r = requests.post(url, data=payload)
    soup = BeautifulSoup(r.content, "html.parser")
    # Get the three hidden parameter values.
    inputs_raw = soup.find_all('input')
    inputs = {x['name']:x['value'] for x in inputs_raw}
    links = soup.find_all(href=re.compile("javascript:__doPostBack\('.*D',''\)"))
    datasets_eventtargets_raw.append((i, inputs, links))

# Get list of files that have already been downloaded.
file_list = set(os.listdir('raw_data/'))

# Loop through the list of tuples and use the payload dict from each tuple to call all the files from the list in that tuple.
pat = re.compile(r"\(\'(.+?)\'\)?")
for tup in datasets_eventtargets_raw:
    # Parse out the argument value and filename (for validating responses).
    datasets_eventtargets = [(pat.findall(x['href'])[0], x.text) for x in tup[2]]
    
    # Get the three common arguments for all the files on this page.
    payload = tup[1]
    
    # Add a blank fourth.
    payload['__EVENTARGUMENT'] = ''
    
    # Loop through the parsed file arguments and request the files.
    for t in datasets_eventtargets:
        if t[1] not in file_list:  # Check if this file has already been downloaded.
            payload['__EVENTTARGET'] = t[0]
            r = requests.post(url, data=payload)
            if get_filename(r.headers) == t[1]:
                # Save the file. 
                # TODO: Should rename the files so year is first so they sort correctly.
                with open(os.path.join(path, get_filename(r.headers)), 'wb') as f:  
                    f.write(r.content)
            else:
                print('Error with page: ' + str(tup[0]) + ', argument: ' + t[0])
            time.sleep(5) #to avoid connection issues with the server
        else:
            print(t[1] + ' has already been downloaded.')


