#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''test_script_prefetch
OAuth2 'credentials_CI.json.enc'
Apps Script Crash Course: Import/Export Apps Script Code
https://www.youtube.com/watch?v=lEVMu9KE6jk
Google Drive SDK: Searching for files
https://www.youtube.com/watch?v=DOSvQmQK_HA
https://developers.google.com/drive/v2/reference/files/list
GET https://www.googleapis.com/drive/v2/files?key={YOUR_API_KEY}
GET https://www.googleapis.com/drive/v2/files?q=mimeTyep%3D%27application%2Fvnd.google-apps.script%27&key={YOUR_API_KEY}
GET https://www.googleapis.com/drive/v2/files?q=mimeTyep%3D%27application%2Fvnd.google-apps.spreadsheet%27&key={YOUR_API_KEY}
'''

import sys, os
import pprint

from oauth2client.anyjson import simplejson
import googleDriveAccess

import logging
logging.basicConfig()
logger = logging.getLogger()

SCRIPT_TYPE = 'application/vnd.google-apps.script+json'

logging.getLogger().setLevel(getattr(logging, 'INFO'))
basedir = os.path.abspath('.')
ci = googleDriveAccess.readClientId(basedir)
ds = googleDriveAccess.second_authorize(basedir, ci, script=True)

def execQuery(q):
  items = ds.files().list(q=q).execute()['items']
  for f in items:
    print f['modifiedDate'], f['title'], f['id'], f['mimeType']

execQuery("title contains 'test'")
execQuery("fullText contains 'test'")
execQuery("'root' in parents") # files and folders in root
execQuery("'root' in parents and fullText contains 'test'") # only in root
execQuery("not 'root' in parents and fullText contains 'test'") # only not root
execQuery("sharedWithMe")
# execQuery("'YOURACCOUNT@gmail.com' in writers")
# execQuery("'YOURACCOUNT@gmail.com' in owners")
execQuery("'root' in parents and modifiedDate > '2014-06-30T23:59:59'")
execQuery("modifiedDate >= '2014-06-30T00:00:00' and modifiedDate < '2014-07-02T00:00:00'")
# execQuery("'test_folder' in parents") # File not found:
# execQuery("'YOUR_FOLDER_ID' in parents") # OK /test_folder
# execQuery("'root/subfolder' in parents") # File not found:
# execQuery("'subfolder' in parents") # File not found:
# execQuery("'subfolder' in 'root'") # Invalid Value
# execQuery("'YOUR_SUBFOLDER_ID' in parents") # OK /subfolder
# execQuery("'YOUR_SUB_SUBFOLDER_ID' in parents") # OK /subfolder/sub_subfolder

e = ds.files().list(q="mimeType='%s'" % SCRIPT_TYPE[:-5]).execute()

# pprint.pprint(e)
# pprint.pprint(e['items'])
# pprint.pprint(e['items'][0])
# pprint.pprint(e['items'][0]['exportLinks'])
# pprint.pprint(e['items'][0]['title'])
# pprint.pprint(e['items'][0]['content']['type']) # KeyError: 'content'
# pprint.pprint(e['items'][0]['contents']['type']) # KeyError: 'contents'
# pprint.pprint(e['items'][0]['type']) # KeyError: 'type'
# pprint.pprint(e['items'][0]['mimeType']) # application/vnd.google-apps.script

download_url = e['items'][0]['exportLinks'][SCRIPT_TYPE]
resp, content = ds._http.request(download_url)
if resp.status != 200: raise Exception('An error occurred: %s' % resp)
data = simplejson.loads(content)

pprint.pprint(data['files'])
pprint.pprint(data['files'][0])
pprint.pprint(data['files'][0]['name'])
pprint.pprint(data['files'][0]['type'])
pprint.pprint(data['files'][0]['source'])

# pprint.pprint(data['files'][0].__dict__) # AttributeError:
