#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''encrypt_client_secret
encrypt client_secret_CI.json to client_secret_CI.json.enc
and delete original plain text file client_secret_CI.json
read CI from cicache.txt
'''

import sys, os
import socket
import getpass
import googleDriveAccess as gda
import logging
logging.basicConfig()

CLIENT_SECRET = 'client_secret'

def encrypt_client_secret(basedir):
  ci = gda.readClientId(basedir)
  cs = os.path.join(basedir, '%s_%s.json' % (CLIENT_SECRET, ci))
  if not os.path.exists(cs):
    sys.stderr.write('file does not exists: %s' % cs)
    return
  f = open(cs, 'rb')
  j = f.read()
  f.close()
  print 'encrypt %s_CI.json to %s_CI.json.enc' % (CLIENT_SECRET, CLIENT_SECRET)
  pid = gda.getpass2()
  gda.storeJsonClient(basedir, pid, ci, j)
  ecs = '%s.enc' % cs
  if os.path.exists(ecs):
    os.remove(cs)

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    encrypt_client_secret(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
