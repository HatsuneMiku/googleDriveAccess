#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''test_folder_hierarchy
'''

import sys, os
import socket

from oauth2client.anyjson import simplejson
import googleDriveAccess

import logging
logging.basicConfig()

FOLDER_TYPE = 'application/vnd.google-apps.folder'

def uenc(u):
  if isinstance(u, unicode): return u.encode('utf-8')
  else: return u

def walk(da, folderId, outf, depth, topdown=True):
  spc = ' ' * (len(depth) - 1)
  outf.write('%s+%s\n%s %s\n' % (
    spc, uenc(folderId), spc, '/'.join(depth + ('', ))))

  def outfiles(da, folderId, outf, spc):
    q = "'%s' in parents and mimeType!='%s'" % (folderId, FOLDER_TYPE)
    entries = da.execQuery(q, True, True, **{'maxResults': 200})
    for f in entries['items']:
      outf.write('%s -%s %s\n%s  %s\n' % (
        spc, uenc(f['id']), uenc(f['mimeType']), spc, uenc(f['title'])))

  if topdown: outfiles(da, folderId, outf, spc)
  q = "'%s' in parents and mimeType='%s'" % (folderId, FOLDER_TYPE)
  entries = da.execQuery(q, True, True, **{'maxResults': 200})
  for folder in entries['items']:
    walk(da, folder['id'], outf, depth + (folder['title'], ))
  if not topdown: outfiles(da, folderId, outf, spc)

def visitCallback(arg, epaths, edirs, efiles=None):
  outf = arg[0]
  spc = ' ' * (len(epaths) - 1)
  joinedepaths = '/'.join(map(lambda a: uenc(a[1]), epaths))
  if efiles is None:
    outf.write('%s+%s\n%s %s/\n' % (
      spc, uenc(epaths[-1][2]), spc, joinedepaths))
  else:
    for ef in efiles:
      outf.write('%s -%s %s\n%s  %s/%s\n' % (
        spc, uenc(ef[2]), uenc(ef[3]), spc, joinedepaths, uenc(ef[1])))

def proc_iter(outf, epaths, edirs, efiles, topdown=True):
  spc = ' ' * len(epaths)
  joinedepaths = '/'.join(map(lambda a: uenc(a[1]), epaths))

  def outfiles(outf, efiles, spc, joinedepaths):
    for ef in efiles:
      outf.write('%s-%s %s\n%s %s/%s\n' % (
        spc, uenc(ef[2]), uenc(ef[3]), spc, joinedepaths, uenc(ef[1])))

  if topdown: outfiles(outf, efiles, spc, joinedepaths)
  for ed in edirs:
    outf.write('%s+%s\n%s %s/%s/\n' % (
      spc, uenc(ed[2]), spc, joinedepaths, uenc(ed[1])))
  if not topdown: outfiles(outf, efiles, spc, joinedepaths)

def main(basedir):
  da = googleDriveAccess.DAClient(basedir) # clientId=None, script=False

  f = open(os.path.join(basedir, 'hierarchy_topdown.txt'), 'wb')
  walk(da, 'root', f, ('', ))
  f.close()
  f = open(os.path.join(basedir, 'hierarchy_bottomup.txt'), 'wb')
  walk(da, 'root', f, ('', ), topdown=False)
  f.close()

  f = open(os.path.join(basedir, 'hierarchy_visit_topdown.txt'), 'wb')
  da.walk_visit('root', visitCallback, [f])
  f.close()
  f = open(os.path.join(basedir, 'hierarchy_visit_bottomup.txt'), 'wb')
  da.walk_visit('root', visitCallback, [f], topdown=False)
  f.close()

  f = open(os.path.join(basedir, 'hierarchy_iter_topdown.txt'), 'wb')
  for epaths, edirs, efiles in da.walk_iter('root'):
    proc_iter(f, epaths, edirs, efiles)
  f.close()
  f = open(os.path.join(basedir, 'hierarchy_iter_bottomup.txt'), 'wb')
  for epaths, edirs, efiles in da.walk_iter('root', topdown=False):
    proc_iter(f, epaths, edirs, efiles, topdown=False)
  f.close()

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    main(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
