#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''test_spreadsheet_factory
'''

import sys, os
import socket
import pprint

import googleDriveAccess as gda

import logging
logging.basicConfig()

SHEET_NAME = 'test_spreadsheet_factory'

def main(basedir):
  ss = gda.SpreadsheetFactory(basedir)(sheetName=SHEET_NAME)
  print ss.oa2act
  print ss.sheetId
  print ss.sheet()['title']
  for ws in ss.worksheets():
    print u'%s : %s' % (ws.get_worksheet_id(), ws.title.text)
  for cell in ss.cells():
    print u'%s : %s' % (cell.title.text, cell.content.text)

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    main(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
