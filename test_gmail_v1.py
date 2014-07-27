#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''test_gmail_v1
message will be in 'SENT' label
so add labels 'INBOX', 'UNREAD', 'STARRED' later
'''

import sys, os
import socket
import pprint

import googleDriveAccess as gda

import logging
logging.basicConfig()

def main(basedir):
  oa2 = gda.OAuth2Client(basedir)
  ui = oa2.userInfo()
  act = ui['email']
  gm = gda.GmailClient(abc=oa2)
  mo = gm.sendMsg(act, act, 'message title', 'message text')
  # pprint.pprint(mo)
  if mo:
    print 'MessageId: %s - labels %s' % (mo['id'], mo['labelIds'])
    mo = gm.modifyLabels(mo['id'], addLabels=['INBOX', 'UNREAD', 'STARRED'])
    print 'MessageId: %s - labels %s' % (mo['id'], mo['labelIds'])
  mo = gm.sendMsg(act, act, 'title attach', 'text attach', 'test_document.txt')
  # pprint.pprint(mo)
  if mo:
    print 'MessageId: %s - labels %s' % (mo['id'], mo['labelIds'])
    mo = gm.modifyLabels(mo['id'], addLabels=['INBOX', 'UNREAD', 'STARRED'])
    print 'MessageId: %s - labels %s' % (mo['id'], mo['labelIds'])

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    main(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
