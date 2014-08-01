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

def download_file(basedir, filename, mimetype):
  da = gda.DAClient(basedir, script=True) # clientId=None
  fileinfo = (filename, mimetype)
  q = "title contains '%s' and mimeType='%s'" % fileinfo
  entries = da.execQuery(q, noprint=True, maxResults=2)
  cnt = len(entries['items'])
  if not cnt:
    sys.stderr.write('not found [%s] %s\n' % fileinfo)
    return
  if cnt > 1:
    sys.stderr.write('duplicated [%s] %s\a\n' % fileinfo)
  # pprint.pprint(entries)
  fileObj = entries['items'][0]
  for k in ('id', 'mimeType', 'title', 'description'):
    print u'%s: %s' % (k, fileObj[k])
  fileId, fileObj = da.downloadFile(basedir, filename, fileObj['id'], mimetype)
  print u'id: %s' % fileId

def main(basedir):
  download_file(basedir, FILENAME, 'text/plain')

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    main(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
