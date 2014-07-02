#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''test_script_import_export
OAuth2 'credentials_CI.json.enc'
Apps Script Crash Course: Import/Export Apps Script Code
https://www.youtube.com/watch?v=lEVMu9KE6jk
Google Drive SDK: Searching for files
https://www.youtube.com/watch?v=DOSvQmQK_HA
https://developers.google.com/drive/v2/reference/files/list
GET https://www.googleapis.com/drive/v2/files?key={YOUR_API_KEY}
GET https://www.googleapis.com/drive/v2/files?q=mimeTyep%3D%27application%2Fvnd.google-apps.script%27&key={YOUR_API_KEY}
GET https://www.googleapis.com/drive/v2/files?q=mimeTyep%3D%27application%2Fvnd.google-apps.spreadsheet%27&key={YOUR_API_KEY}
import: upload
export: download
'''

import sys, os
import socket
import pprint

import googleDriveAccess

import logging
logging.basicConfig()

SCRIPT_FOLDER = 'script_import_export'
SCRIPT_ID = 'SCRIPT_ID_YOU_WISH_TO_HANDLE'
SCRIPT_NAME = 'test_GoogleAppsScript_createCalendarEvent'

def main(basedir):
  folder = os.path.join(basedir, SCRIPT_FOLDER)
  das = googleDriveAccess.DAScript(basedir, folder) # clientId=None
  mode = 0 # 0: create, 1: upload, 2: download
  if mode == 0: id, fileobj = das.upload(None, SCRIPT_NAME, create=True)
  elif mode == 1: id, fileobj = das.upload(SCRIPT_ID, SCRIPT_NAME)
  else: id, fileobj = das.download(SCRIPT_ID)
  pprint.pprint(fileobj)
  print 'SCRIPT_ID=%s' % id

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    main(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
