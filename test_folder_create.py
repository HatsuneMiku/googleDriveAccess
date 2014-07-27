#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''test_folder_create
googleDriveAccess.DAClient.makeDirs(folder)
  folder must start with '/'
  returns id string, folder string
googleDriveAccess.DAClient.createFolder(name)
  name must *NOT* contain '/'
  returns id string, folder Object
'''

import sys, os
import socket
import pprint

import googleDriveAccess as gda

import logging
logging.basicConfig()

FOLDER_TEST = 'this_is_a_test_folder'
FOLDER_NAME = 'GoogleAppsScript_demo'

def main(basedir):
  da = gda.DAClient(basedir) # clientId=None, script=False
  id, folder = da.createFolder(FOLDER_TEST) # parentId='root'
  pprint.pprint(folder)
  print 'FOLDER_ID=%s [%s]' % (id, folder['title'])

  id, q = da.makeDirs('/%s/%s' % (FOLDER_TEST, FOLDER_NAME))
  print 'FOLDER_ID=%s [%s]' % (id, q)

  # test for bottomup directory creation
  for subfolder in ['sub1/sub2', 'sub1/sub3', 'sub4']:
    p_id, q = da.makeDirs('/%s/testbottomup/%s' % (FOLDER_TEST, subfolder))
    print 'FOLDER_ID=%s [%s]' % (p_id, q)

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    main(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
