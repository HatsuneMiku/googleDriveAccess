#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''test_folder_create
'''

import sys, os
import socket
import pprint

import googleDriveAccess

import logging
logging.basicConfig()

FOLDER_NAME = 'test_GoogleAppsScripts'

def main(basedir):
  da = googleDriveAccess.DAClient(basedir) # clientId=None, script=False
  id, folder = da.createFolder(FOLDER_NAME) # parentId='root'
  pprint.pprint(folder)
  print 'FOLDER_ID=%s' % id

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    main(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
