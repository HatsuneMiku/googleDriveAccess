#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''recursive_upload
This program creates so many directories and files to remote Google Drive.
But you should upload them into an archive (.tar.gz).
'''

import sys, os
import socket

import googleDriveAccess

import logging
logging.basicConfig()

BACKUP = 'recursive_upload_backup'

def main(basedir):
  da = googleDriveAccess.DAClient(basedir)
  da.recursiveUpload(BACKUP)
  # test for bottomup directory creation
  for subfolder in ['sub1/sub2', 'sub1/sub3', 'sub4']:
    p_id, q = da.prepare_folder('/%s/testbottomup/%s' % (BACKUP, subfolder))

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    main(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
