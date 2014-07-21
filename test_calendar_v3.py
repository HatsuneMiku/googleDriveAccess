#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''test_calendar_v3
'''

import sys, os
import time
import googleDriveAccess
from apiclient.discovery import build
import pprint

TEST_TITLE = u'test 予定 python api' # unicode
# you may use pytz.timezone() and datetime.datetime.now(pytz.utc)
TZ = 'Asia/Tokyo' # or may be '+09:00' is ok, but can not use string 'JST-9'

def isoTime(t):
  if False: # returns no 'timeZone' to use locale timezone of google calendar ?
    dt = time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.gmtime(t))
    return {'dateTime': dt}
  else:
    # dt = time.strftime('%Y-%m-%dT%H:%M:%S+09:00', time.localtime(t))
    dt = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(t)) # assume TZ
    return {'dateTime': dt, 'timeZone': TZ}

def isoDate(t):
  dt = time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.gmtime(t))
  return {'date': dt[:10]}

da = googleDriveAccess.DAClient(os.path.abspath('.'))
calendar_service = build('calendar', 'v3', http=da.http)
cals = calendar_service.calendarList().list().execute()
# pprint.pprint(cals)
for cal in cals['items']:
  print u'%s : %s' % (cal['id'], cal['summary']) # unicode

print u'================================================================'
id = cals['items'][0]['id']
evt1 = { # date only
  'start': isoDate(time.time()), 'end': isoDate(time.time() + 24 * 3600),
  'location': u'皇居', 'summary': TEST_TITLE} # unicode
evtObj = calendar_service.events().insert(calendarId=id, body=evt1).execute()
# pprint.pprint(evtObj)
evt2 = { # date and time
  'start': isoTime(time.time() + 1800), 'end': isoTime(time.time() + 3600),
  'location': u'京都御所', 'summary': TEST_TITLE} # unicode
evtObj = calendar_service.events().insert(calendarId=id, body=evt2).execute()
# pprint.pprint(evtObj)

for cal in cals['items']:
  print u'================================================================'
  entries = calendar_service.events().list(calendarId=cal['id']).execute()
  # pprint.pprint(entries)
  print u'entry : %s' % (entries['summary']) # unicode
  for ev in entries['items']:
    if 'date' in ev['start']:
      s, e = ev['start']['date'], ev['end']['date'] # test evt1
    else:
      s, e = ev['start']['dateTime'], ev['end']['dateTime'] # test evt2
    print u'%s : %s : %s' % (s, e, ev['summary']) # unicode
    if ev['summary'] == TEST_TITLE: # unicode
      pprint.pprint(ev)
      print u'----------------------------------------------------------------'

