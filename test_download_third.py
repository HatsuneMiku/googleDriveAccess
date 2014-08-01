#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''test_download_third
OAuth2 and save / load credentials to / from 'credentials_CI_OA2ACT.json.enc'
Apps Script Crash Course: Import/Export Apps Script Code
https://www.youtube.com/watch?v=lEVMu9KE6jk
'''

import sys, os
import socket
import pprint

import googleDriveAccess as gda

import logging
logging.basicConfig()

FILENAME = 'test_document.txt'

def print_file((fileId, fileObj)):
  # pprint.pprint(fileObj)
  # print u'id: %s' % fileId
  for k in ('id', 'mimeType', 'title', 'description'):
    print u'%s: %s' % (k, fileObj[k])

def download_file(basedir, filename, mimetype):
  da = gda.DAClient(basedir, script=True) # clientId=None

  # 101 test search mimetype in parent
  fileInfo = da.downloadFile(basedir, filename, 'root', mimetype=mimetype)
  print_file(fileInfo)

  # 001 test search mimetype
  print_file(da.downloadFile(basedir, filename, None, mimetype=mimetype))

  fileId = fileInfo[0]

  # 111 test fileId (ignore) mimetype in parent
  print_file(da.downloadFile(basedir, filename, 'root', fileId, mimetype))

  # 011 test fileId (ignore) mimetype
  print_file(da.downloadFile(basedir, filename, None, fileId, mimetype))

  # 110 test fileId (ignore) in parent
  print_file(da.downloadFile(basedir, filename, 'root', fileId))

  # 010 test fileId
  print_file(da.downloadFile(basedir, filename, None, fileId))

  # 100 test search in parent
  print_file(da.downloadFile(basedir, filename, parentId='root'))

  # 000 test search
  print_file(da.downloadFile(basedir, filename, parentId=None))

def main(basedir):
  download_file(basedir, FILENAME, 'text/plain')

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    main(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
