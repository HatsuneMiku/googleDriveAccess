#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''recursive_upload
This program creates so many directories and files to remote Google Drive.
But you should upload them into an archive (.tar.gz).
'''

import sys, os
import socket

import googleDriveAccess as gda

import logging
logging.basicConfig()

BACKUP = 'recursive_upload_backup'

def main(basedir):
  da = gda.DAClient(basedir)
  da.recursiveUpload(BACKUP)

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    main(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
