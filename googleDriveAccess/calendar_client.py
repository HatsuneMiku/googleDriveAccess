#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''calendar_client
'''

import sys, os
import time

from abstract_client import AbstractClient

class CalendarClient(AbstractClient):
  srv_name = 'calendar'
  srv_version = 'v3'

  def __init__(self, tz='UTC', basedir=None, **kwargs):
    '''you may use pytz.timezone() and datetime.datetime.now(pytz.utc)'''
    super(CalendarClient, self).__init__(basedir, **kwargs)
    self.tz = tz

  def isoTime(self, t):
    if False: # returns no 'timeZone' to use locale timezone of google calendar
      dt = time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.gmtime(t))
      return {'dateTime': dt}
    else:
      # dt = time.strftime('%Y-%m-%dT%H:%M:%S+09:00', time.localtime(t))
      dt = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(t)) # assume TZ
      return {'dateTime': dt, 'timeZone': self.tz}

  def isoDate(self, t):
    # dt = time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.gmtime(t)) # *** BUG ?
    dt = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(t)) # assume TZ
    return {'date': dt[:10]}

  def startend(self, ev):
    if 'date' in ev['start']: # date only
      return (True, ev['start']['date'], ev['end']['date'])
    else: # date and time
      return (False, ev['start']['dateTime'], ev['end']['dateTime'])

  def idList(self):
    return self.service.calendarList().list().execute()

  def eventList(self, id):
    return self.service.events().list(calendarId=id).execute()

  def insertEvent(self, id, **kwargs):
    '''
    id: calendar id
    start: ca.isoDate(st) or ca.isoTime(st)
    end: ca.isoDate(et) or ca.isoTime(et)
    location: u'unicode string'
    summary: u'unicode string'
    '''
    return self.service.events().insert(calendarId=id, body=kwargs).execute()
