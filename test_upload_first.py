#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''test_upload_first
OAuth2 and save credentials to 'credentials_CI_OA2ACT.json.enc'
Apps Script Crash Course: Import/Export Apps Script Code
https://www.youtube.com/watch?v=lEVMu9KE6jk
'''

import sys, os
import socket

import googleDriveAccess as gda

import logging
logging.basicConfig()

def main(basedir):
  da = gda.DAClient(basedir, script=True, firstonly=True)
  da.first_authorize()

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    main(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
