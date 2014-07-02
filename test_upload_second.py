#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''test_upload_second
OAuth2 and save / load credentials to / from 'credentials.json.enc'
Apps Script Crash Course: Import/Export Apps Script Code
https://www.youtube.com/watch?v=lEVMu9KE6jk
'''

import sys, os
import socket
import pprint

from apiclient.http import MediaFileUpload
import googleDriveAccess

import logging
logging.basicConfig()

FILENAME = 'test_document.txt'

def upload_file(basedir, filename, mimetype, description):
  ci = googleDriveAccess.readClientId(basedir)
  drive_service = googleDriveAccess.second_authorize(basedir, ci)

  # Upload a file
  body = {'title': filename, 'mimeType': mimetype, 'description': description}
  mbody = MediaFileUpload(filename, mimetype=mimetype, resumable=True)
  fileobj = drive_service.files().insert(body=body, media_body=mbody).execute()
  pprint.pprint(fileobj)

def main(basedir):
  upload_file(basedir, FILENAME, 'text/plain', 'this is a test')

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    main(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
