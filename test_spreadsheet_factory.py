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

def trimWidth(s, m=72):
  from unicodedata import east_asian_width
  L = {'Na': 1, 'W': 2, 'F': 2, 'H': 1, 'A': 2, 'N': 1}
  u, w = [], 0
  for c in s:
    w += L[east_asian_width(c)]
    if w > m: break
    u.append(c)
  return u''.join(u)

def main(basedir):
  ss = gda.SpreadsheetFactory(basedir)(sheetName=SHEET_NAME)
  print ss.oa2act
  print ss.sheet()['title']
  print ss.sheetId
  print ss.worksheetId
  for ws in ss.worksheets():
    id_uri = ws.get_id()
    uri_base, sheetId, worksheetId = id_uri.rsplit('/', 2)
    print u'%s : %s : %s' % (sheetId, ws.get_worksheet_id(), ws.title.text)
  cells = ss.cells()
  for n, cell in enumerate(cells):
    # print u'%s : %s' % (cell.title.text, cell.content.text)
    print u'    %4d %4s %3d %3d %-8s' % (n, cell.title.text,
      int(cell.cell.row), int(cell.cell.col), cell.content.text)

  # change True when you get a version (2013-07-12) after gdata-2.0.18
  # https://code.google.com/p/gdata-python-client/source/list
  if False:
    ss.updateCell(1, 1, u'日本語表示')
    ss.updateCell(3, 3, u'漢字')

  print u'-' * 72
  j, c = -1, 0
  for n, cell in enumerate(cells):
    k = int(cell.cell.row) - 1
    if k != j:
      j = k
      if j: sys.stdout.write('\n')
      c = 0
    # *** will be skipped many cells that has no data ***
    col = int(cell.cell.col)
    c += 1
    while c < col:
      sys.stdout.write(' ' * 13)
      c += 1
    print trimWidth(u'%-12s' % cell.content.text, 12),
  if j: sys.stdout.write('\n')

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    main(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
