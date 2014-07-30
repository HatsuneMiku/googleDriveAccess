#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''test_calendar_v3
'''

import sys, os
import socket
import pprint

import time
import googleDriveAccess as gda
from apiclient.discovery import build

import logging
logging.basicConfig()

TEST_TITLE = u'test 予定 python api' # unicode
# you may use pytz.timezone() and datetime.datetime.now(pytz.utc)
TZ = 'Asia/Tokyo' # or may be '+09:00' is ok, but can not use string 'JST-9'

def main(basedir):
  ca = gda.CalendarClient(TZ, basedir)
  cals = ca.idList()
  # pprint.pprint(cals)
  for cal in cals['items']:
    print u'%s : %s' % (cal['id'], cal['summary']) # unicode

  print u'=' * 64
  id = cals['items'][0]['id']
  t = time.time()
  evtObj = ca.insertEvent(id,
    start=ca.isoDate(t), end=ca.isoDate(t + 24 * 3600), # date only
    location=u'皇居', summary=TEST_TITLE) # unicode
  # pprint.pprint(evtObj)
  evtObj = ca.insertEvent(id,
    start=ca.isoTime(t + 1800), end=ca.isoTime(t + 3600), # date and time
    location=u'京都御所', summary=TEST_TITLE) # unicode
  # pprint.pprint(evtObj)

  for cal in cals['items']:
    print u'=' * 64
    entries = ca.eventList(cal['id'])
    # pprint.pprint(entries)
    print u'entry : %s' % (entries['summary']) # unicode
    for ev in entries['items']:
      b, s, e = ca.startend(ev)
      print u'%s : %s : %s' % (s, e, ev['summary']) # unicode
      if ev['summary'] == TEST_TITLE: # unicode
        pprint.pprint(ev)
        print u'-' * 64

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    main(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
