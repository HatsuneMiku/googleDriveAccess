#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''spreadsheet_factory
'''

import sys, os
import httplib2
from gdata.spreadsheets.client import SpreadsheetsClient
from oauth2client_gdata_bridge import OAuth2BearerToken
from oauth2client.client import AccessTokenRefreshError
from oauth2client.anyjson import simplejson
# import simplejson

from abstract_client import SPREADSHEET_TYPE
from da_client import DAClient

class SpreadsheetFactory(DAClient):
  def __init__(self, basedir=None, **kwargs):
    super(SpreadsheetFactory, self).__init__(basedir, **kwargs)
    self.ssc = self.getSpreadsheetsClient()

  def getSpreadsheetsClient(self):
    return SpreadsheetsClient(auth_token=OAuth2BearerToken(self.credentials))

  def __call__(self, **kwargs):
    '''
    sheetName: search sheet
    parentId: search sheet from parent
    sheetId: ignore sheetName and parentId when set this
    '''
    self.sheetName = kwargs.get('sheetName', None)
    self.parentId = kwargs.get('parentId', None)
    self.sheetId = kwargs.get('sheetId', None)
    self.worksheetId = None
    self.set_activesheet()
    return self

  def set_activesheet(self):
    if self.sheetId is None:
      q = "mimeType='%s'" % SPREADSHEET_TYPE
      if self.sheetName: q = "%s and title contains '%s'" % (q, self.sheetName)
      if self.parentId: q = "%s and '%s' in parents" % (q, self.parentId)
      entries = self.execQuery(q, noprint=True)
      if not len(entries['items']):
        sys.stderr.write('not found: %s\n' % q)
        return
      self.sheetId = entries['items'][0]['id']
    for ws in self.worksheets():
      self.worksheetId = ws.get_worksheet_id()
      break

  def sheet(self, sheetId=None):
    if sheetId is None: sheetId = self.sheetId
    return self.service.files().get(fileId=sheetId).execute()

  def worksheets(self, sheetId=None):
    '''
    sheetId:
    '''
    if sheetId is None: sheetId = self.sheetId
    return self.ssc.get_worksheets(sheetId).entry

  def cells(self, sheetId=None, worksheetId=None):
    '''
    sheetId:
    worksheetId:
    '''
    if sheetId is None: sheetId = self.sheetId
    if worksheetId is None: worksheetId = self.worksheetId
    return self.ssc.get_cells(sheetId, worksheetId).entry
