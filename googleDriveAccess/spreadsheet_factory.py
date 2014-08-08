#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''spreadsheet_factory
gdata.spreadsheets.client.SpreadsheetsClient by OAuth2 auth_token
https://code.google.com/p/gdata-python-client/source/browse/src/gdata/spreadsheets/client.py
gdata.spreadsheet.text_db.DatabaseClient has no auth_token parameter
https://code.google.com/p/gdata-python-client/source/browse/src/gdata/spreadsheet/text_db.py
'''

import sys, os
import httplib2
from apiclient.http import MediaInMemoryUpload
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
    self.bearerToken = OAuth2BearerToken(self.credentials)
    self.ssc = SpreadsheetsClient(auth_token=self.bearerToken)

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
      q = ["mimeType='%s'" % SPREADSHEET_TYPE]
      if self.sheetName: q.append("title contains '%s'" % self.sheetName)
      if self.parentId: q.append("'%s' in parents" % self.parentId)
      q.append('explicitlyTrashed=False')
      entries = self.execQuery(' and '.join(q), noprint=True)
      if not len(entries['items']):
        self.sheetId = None
        self.worksheetId = None
        sys.stderr.write('not found: %s\n' % q)
        return
      self.sheetId = entries['items'][0]['id']
    for ws in self.worksheets():
      self.worksheetId = ws.get_worksheet_id()
      break
    else:
      self.worksheetId = None

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

  def updateCell(self, row, col, val, sheetId=None, worksheetId=None):
    '''
    packaged version of gdata-2.0.18 does NOT contain update_cell()
    (pip install gdata) or (easy_install gdata)
    version (2013-07-12) some functions are added after gdata-2.0.18
    https://code.google.com/p/gdata-python-client/source/list
    please clone new version (python setup.py install)
    hg clone https://code.google.com/p/gdata-python-client/

    and bug is reported: http://stackoverflow.com/questions/9940578/
    add parameter force=True to fix it
    '''
    if sheetId is None: sheetId = self.sheetId
    if worksheetId is None: worksheetId = self.worksheetId
    return self.ssc.update_cell(sheetId, worksheetId, row, col, val, force=True)

  def createSpreadsheet(self, sheetName, description=None, parentId=None,
    csv=None, rows=1000, cols=26):
    '''
    sheetName: file name for Google Drive
    description: description for Google Drive (default same as sheetName)
    parentId: create into parent folder (default 'root')
    csv: string (default None: empty sheet)
    rows: int (default 1000)
    cols: int (default 26)
    '''
    body = {'title': sheetName, 'mimeType': 'text/csv', # to be converted
      'description': description if description else sheetName}
    if parentId is None: parentId = 'root'
    body['parents'] = [{'id': parentId}]
    line = [',' * cols]
    if csv:
      lines = csv.splitlines()
      dat = lines + (line * (rows - len(lines)))
    else:
      dat = line * rows
    mbody = MediaInMemoryUpload('\n'.join(dat),
      mimetype='text/csv', chunksize=256*1024, resumable=False)
    req = self.service.files().insert(body=body, media_body=mbody)
    req.uri += '&convert=true'
    fileObj = req.execute()
    if fileObj is None: return (None, None)
    self.sheetId = fileObj['id']
    self.set_activesheet()
    return (self.sheetId, fileObj)
