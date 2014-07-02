#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''test_upload_first
OAuth2 and save credentials to 'credentials.json.enc'
Apps Script Crash Course: Import/Export Apps Script Code
https://www.youtube.com/watch?v=lEVMu9KE6jk
'''

import sys, os
import socket

import googleDriveAccess

import logging
logging.basicConfig()

def main(basedir):
  da = googleDriveAccess.DAClient(basedir, script=True, firstonly=True)
  da.first_authorize()

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    main(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
