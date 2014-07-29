#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''googleDriveAccess
Apps Script Crash Course: Import/Export Apps Script Code
https://www.youtube.com/watch?v=lEVMu9KE6jk
Google Drive SDK: Searching for files
https://www.youtube.com/watch?v=DOSvQmQK_HA
'''

import sys, os

def getConf(conf_file):
  return open(conf_file, 'rb').read().splitlines()

__conf__ = getConf(os.path.join(os.path.dirname(__file__), 'conf/setup.cf'))
__version__ = __conf__[0]
__url__ = 'https://github.com/HatsuneMiku/googleDriveAccess'
__author__ = '999hatsune'
__author_email__ = '999hatsune@gmail.com'

import time
import sqlite3
import getpass
from StringIO import StringIO
import base64
import bz2

import httplib2
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from apiclient import errors
from oauth2client.client import OAuth2WebServerFlow, OAuth2Credentials
from oauth2client.anyjson import simplejson
# import simplejson

from buf_AES_256_CBC import buf_AES_256_CBC_decrypt, buf_AES_256_CBC_encrypt

import logging

OAUTH_SCOPE = __conf__[2:]

CICACHE_FILE = 'cicache.txt'
CLIENT_FILE = 'client_secret_%s.json.enc'
CREDENTIAL_FILE = 'credentials_%s_%s.json.enc'
CACHE_FOLDERIDS = 'cache_folderIds_%s_%s.sl3'
MAX_ACT_LEN = 256
MAX_KEY_LEN = 256
MAX_PATH_LEN = 1024

MANIFEST = 'manifest.json'
SCRIPT_TYPE = 'application/vnd.google-apps.script+json'
FOLDER_TYPE = 'application/vnd.google-apps.folder'

def readClientId(basedir):
  f = open(os.path.join(basedir, CICACHE_FILE), 'rb')
  ci = f.readline().strip()
  f.close()
  return ci

def storeClientId(basedir, ci):
  f = open(os.path.join(basedir, CICACHE_FILE), 'wb')
  f.write(ci)
  f.close()

def readJsonClient(basedir, pid, clientId):
  f = open(os.path.join(basedir, CLIENT_FILE % clientId), 'rb')
  enc = StringIO(f.read())
  f.close()
  dec = StringIO()
  buf_AES_256_CBC_decrypt(enc, dec, pid)
  return dec.read()

def storeJsonClient(basedir, pid, clientId, jsonStr):
  dec = StringIO(jsonStr)
  enc = StringIO()
  buf_AES_256_CBC_encrypt(dec, enc, pid)
  f = open(os.path.join(basedir, CLIENT_FILE % clientId), 'wb')
  f.write(enc.read())
  f.close()

def readJsonCredential(pid, fname):
  f = open(fname, 'rb')
  enc = StringIO(f.read())
  f.close()
  dec = StringIO()
  buf_AES_256_CBC_decrypt(enc, dec, pid)
  return bz2.decompress(dec.read())

def storeJsonCredential(pid, fname, jsonStr):
  dec = StringIO(bz2.compress(jsonStr))
  enc = StringIO()
  buf_AES_256_CBC_encrypt(dec, enc, pid)
  f = open(fname, 'wb')
  f.write(enc.read())
  f.close()

def getpass2():
  pid, pid2 = None, None
  while True:
    pid = getpass.getpass()
    print 'once more'
    pid2 = getpass.getpass()
    if pid == pid2: break
    print 'both passwords are not same'
  return pid

class AbstractClient(object):
  '''Base class of Clients'''
  srv_name = None
  srv_version = None

  def __init__(self, basedir=None, **kwargs):
    '''
    basedir: read/write credentials on this directory
    clientId: OAuth2 and save/load credentials with clientId
    oa2act: OAuth2 authorized account replaced to filesystem safe characters
    script: add script to SCOPE
    firstonly: flag not to call second_authorize
    abc: descendant of AbstractClient
    '''
    if self.srv_name is None or self.srv_version is None:
      raise Exception('cannot instanciate AbstractClient')
    self.basedir = basedir
    self.clientId = kwargs.get('clientId', None)
    self.oa2act = kwargs.get('oa2act', None)
    self.script = kwargs.get('script', False)
    self.firstonly = kwargs.get('firstonly', False)
    self.abc = kwargs.get('abc', None)
    if self.abc and not isinstance(self.abc, AbstractClient):
      raise Exception('ancestor of abc must be AbstractClient')
    # for instance
    self.http = self.abc.http if self.abc else None
    self.service = None

    if self.basedir is None:
      if self.abc is None: raise Exception('basedir is None')
      else: self.basedir = self.abc.basedir
    if self.clientId is None: self.clientId = readClientId(self.basedir)
    if self.oa2act is None:
      self.oa2act = self.abc.oa2act if self.abc else 'default'
    else:
      if self.abc:
        if self.oa2act != self.abc.oa2act:
          raise Exception('oa2act is not same as abc.oa2act')
    if self.firstonly: return
    if self.http:
      if self.build(self.http): return
    credentials = self.second_authorize()
    if credentials is None: raise Exception('cannot get credential')
    self.http = credentials.authorize(httplib2.Http())
    if self.build(self.http) is None:
      raise Exception('cannot build Client %s %s' % (
        self.srv_name, self.srv_version))

  def safe_fname(self, fn):
    return fn.replace('@', '.')

  def get_fcred(self, default=False):
    return os.path.join(self.basedir, CREDENTIAL_FILE % (self.clientId,
      'default' if default else self.safe_fname(self.oa2act)))

  def get_stored_credentials(self):
    fcred = self.get_fcred()
    if not os.path.exists(fcred): return None
    print 'open OAuth2 credential for %s CI=%s' % (self.oa2act, self.clientId)
    while True:
      pid = getpass.getpass()
      try:
        credentials = OAuth2Credentials.new_from_json(
          readJsonCredential(pid, fcred))
      except (Exception, ), e:
        credentials = None
      if credentials is None or credentials.invalid:
        n = raw_input('password may be incorrect.\n %s\n %s\n number ?: ' % (
          '1: re-enter password',
          '2: dispose and create new credential for %s' % self.oa2act))
        if n == '2': break
      else:
        self.oa2act = credentials.token_response['id_token']['email']
        break
    return credentials

  def store_credentials(self, credentials):
    self.oa2act = credentials.token_response['id_token']['email']
    print 'OAuth2 success. Enter password to store credential for %s CI=%s' % (
      self.oa2act, self.clientId)
    pid = getpass2()
    storeJsonCredential(pid, self.get_fcred(), credentials.to_json())
    storeJsonCredential(pid, self.get_fcred(True), credentials.to_json())

  def first_authorize(self):
    '''OAuth2 save credentials'''
    print 'client secret open. CI=%s' % self.clientId
    fn = os.path.join(self.basedir, CLIENT_FILE % self.clientId)
    if not os.path.exists(fn): raise Exception('client secret does not exist.')
    while True:
      pid = getpass.getpass()
      try:
        d = readJsonClient(self.basedir, pid, self.clientId)
        cli = simplejson.loads(d)['installed']
      except (Exception, ), e:
        cli = None
      if cli is None: print 'password may be incorrect.'
      else: break
    # pprint.pprint(cli)
    scope = ' '.join(OAUTH_SCOPE[(1 if not self.script else 0):])
    flow = OAuth2WebServerFlow(cli['client_id'], cli['client_secret'],
      scope, redirect_uri=cli['redirect_uris'][0])
    authorize_url = flow.step1_get_authorize_url()
    print 'Go to the following link in your browser: %s' % authorize_url
    code = raw_input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    self.store_credentials(credentials)
    return credentials

  def second_authorize(self):
    '''OAuth2 load credentials'''
    credentials = self.get_stored_credentials()
    if credentials is None or credentials.invalid:
      credentials = self.first_authorize()
    return credentials

  def build(self, http):
    self.service = build(self.srv_name, self.srv_version, http=http)
    return self.service

class OAuth2Client(AbstractClient):
  srv_name = 'oauth2'
  srv_version = 'v2'

  def userInfo(self):
    return self.service.userinfo().get().execute()

class DAClient(AbstractClient):
  srv_name = 'drive'
  srv_version = 'v2'

  def __init__(self, basedir=None, **kwargs):
    self.folderIds = None # will be set in DAClient.build()
    super(DAClient, self).__init__(basedir, **kwargs)
    self.printFields = ['modifiedDate', 'title', 'id', 'mimeType']
    self.printCallback = self.defaultPrintCallback

  def build(self, http):
    '''will be called by AbstractClient.__init__()'''
    super(DAClient, self).build(http)
    self.folderIds = os.path.join(self.basedir,
      CACHE_FOLDERIDS % (self.clientId, self.safe_fname(self.oa2act)))
    self.initializeCacheFolderIds()
    return self.service

  def setPrintFields(self, pfields):
    self.printFields = pfields

  def setPrintCallback(self, pcallback):
    self.printCallback = pcallback

  def defaultPrintCallback(self, e):
    for f in e['items']:
      for fld in self.printFields:
        print f[fld],
      print
    print 'len: %d, hasNext: %s' % (len(e['items']), 'nextPageToken' in e)

  def execQuery(self, q, repeattoken=False, noprint=False, **kwargs):
    '''
    kwargs = {'maxResults': 10} # default maxResults=100
    '''
    result = None
    npt = ''
    while not npt is None:
      if npt != '': kwargs['pageToken'] = npt
      e = self.service.files().list(q=q, **kwargs).execute()
      if result is None: result = e
      else: result['items'] += e['items']
      # e does not have 'nextPageToken' key when len(e['items']) <= maxResults
      npt = e.get('nextPageToken')
      if not noprint and not self.printCallback is None: self.printCallback(e)
      if not repeattoken: break
    return result

  def procentry(self, mode, folderId, q, **kwargs):
    result = []
    c = '=' if mode else '!='
    query = "'%s' in parents and mimeType%s'%s'" % (folderId, c, FOLDER_TYPE)
    entries = self.execQuery(query, True, True, **kwargs)
    for entry in entries['items']:
      result += [map(lambda a: entry[a], self.printFields)]
    return result

  def walk_visit(self, folderId, visit, arg,
    depth=[], topdown=True, q=None, **kwargs):
    '''like os.path.walk()'''
    edirs = self.procentry(True, folderId, q, **kwargs)
    efiles = self.procentry(False, folderId, q, **kwargs)
    if not len(depth):
      depth = [('0000-00-00T00:00:00.000Z', '', folderId, None)]
    visit(arg, depth, edirs)
    if topdown: visit(arg, depth, edirs, efiles)
    for ed in edirs:
      self.walk_visit(ed[2], visit, arg, depth + [ed])
    if not topdown: visit(arg, depth, edirs, efiles)

  def walk_iter(self, folderId, topdown=True, q=None, **kwargs):
    '''like os.walk()'''

    def procfolders(epaths, folders):
      for folder in folders:
        id = folder[2]
        edirs = self.procentry(True, id, q, **kwargs)
        efiles = self.procentry(False, id, q, **kwargs)
        nepaths = epaths + [folder]
        if topdown: yield nepaths, edirs, efiles
        for ep, ed, ef in procfolders(nepaths, edirs):
          yield ep, ed, ef
        if not topdown: yield nepaths, edirs, efiles

    epaths = []
    folders = [('0000-00-00T00:00:00.000Z', '', folderId, None)]
    for ep, ed, ef in procfolders(epaths, folders):
      yield ep, ed, ef

  def initializeCacheFolderIds(self):
    if os.path.exists(self.folderIds):
      cn = sqlite3.connect(self.folderIds)
      try:
        cn.execute('select * from oauth2acts where id=1;')
        checkVersion = True
      except (Exception, ), e:
        checkVersion = False
      cn.close()
      if not checkVersion:
        raise Exception('%s is old version, please delete it' % self.folderIds)
      return
    cn = sqlite3.connect(self.folderIds)
    cn.execute('''\
create table oauth2acts (
 id integer primary key autoincrement,
 oauth2act varchar(%d) unique not null,
 credentials text default '');''' % (
      MAX_ACT_LEN))
    cn.execute('''\
create unique index oauth2acts_idx_oauth2act on oauth2acts (oauth2act);''')
    cn.execute('''\
insert into oauth2acts (oauth2act, credentials) values (?, ?);''', (
      self.oa2act, ''))
    cn.execute('''\
create table folderIds (
 key varchar(%d) primary key not null,
 val varchar(%d) unique not null,
 act integer default 1,
 fol integer default 1,
 flg integer default 0);''' % (
      MAX_KEY_LEN, MAX_PATH_LEN))
    cn.execute('''\
create unique index folderIds_idx_val on folderIds (val);''')
    cn.execute('''\
create index folderIds_idx_act on folderIds (act);''')
    cn.execute('''\
insert into folderIds (key, val) values ('root', '/');''')
    cn.commit()
    cn.close()

  def makeDirs(self, folder):
    '''folder must start with '/'
    returns id string, folder string
    '''
    return self.prepare_folder(folder)

  def createFolder(self, name, parentId='root'):
    '''name must *NOT* contain '/'
    returns id string, folder Object
    '''
    body = {'title': name, 'mimeType': FOLDER_TYPE, 'description': name}
    body['parents'] = [{'id': parentId}]
    folder = self.service.files().insert(body=body).execute()
    return (folder['id'], folder)

  def uploadFile(self, path, filename, parentId, fileId=None):
    # body = {'title': filename, 'mimeType': mimetype, 'description': filename}
    body = {'title': filename, 'description': filename}
    body['parents'] = [{'id': parentId}]
    filepath = os.path.join(path, filename)
    # mbody = MediaFileUpload(filepath, mimetype=mimetype, resumable=True)
    mbody = MediaFileUpload(filepath, resumable=True)
    if mbody._mimetype is None: mbody._mimetype = 'application/octet-stream'
    if fileId is None:
      fileObj = self.service.files().insert(
        body=body, media_body=mbody).execute()
    else:
      fileObj = self.service.files().update(
        fileId=fileId, body=body, media_body=mbody).execute()
    return (fileObj['id'], fileObj)

  def prepare_folder(self, folder):
    q = folder.replace('\\', '/')
    if len(q) > MAX_PATH_LEN:
      raise Exception('folder length is too long > %s' % MAX_PATH_LEN)
    if q[0] != '/':
      raise Exception('folder does not start with / [%s]' % folder)
    if q[-1] == '/' or not len(q): # root or endswith '/'
      return ('root', '/')
    cn = sqlite3.connect(self.folderIds)
    cn.row_factory = sqlite3.Row
    cur = cn.cursor()
    cur.execute('''\
select key from folderIds where val=? and act=? and fol=? and flg=?;''', (
      q, 1, 1, 0))
    row = cur.fetchone()
    cur.close()
    cn.close()
    if row is None:
      parent, p = os.path.split(q)
      parentId, r = self.prepare_folder(parent)
      query = "'%s' in parents and title='%s' and mimeType='%s' %s" % (
        parentId, p, FOLDER_TYPE, 'and explicitlyTrashed=False')
      entries = self.execQuery(query, True, True, **{'maxResults': 2})
      if not len(entries['items']):
        folderId, folderObj = self.createFolder(p, parentId)
      else:
        folderId = entries['items'][0]['id']
        if len(entries['items']) > 1:
          sys.stderr.write('duplicated folder [%s]\a\n' % q)
      cn = sqlite3.connect(self.folderIds)
      cn.execute('''\
insert into folderIds (key, val, act, fol, flg) values (?, ?, ?, ?, ?);''', (
        folderId, q, 1, 1, 0))
      cn.commit()
      cn.close()
    else:
      folderId = row['key']
    return (folderId, q)

  def process_file(self, path, filename, parentId, parent):
    cn = sqlite3.connect(self.folderIds)
    cn.row_factory = sqlite3.Row
    cur = cn.cursor()
    cur.execute('''\
select key from folderIds where val=? and act=? and fol=? and flg=?;''', (
      '%s/%s' % (parent, filename), 1, 0, 0))
    row = cur.fetchone()
    cur.close()
    cn.close()
    if row is None:
      query = "'%s' in parents and title='%s' and mimeType!='%s' %s" % (
        parentId, filename, FOLDER_TYPE, 'and explicitlyTrashed=False')
      entries = self.execQuery(query, True, True, **{'maxResults': 2})
      if not len(entries['items']):
        fileId, fileObj = self.uploadFile(path, filename, parentId)
      else:
        fileId = entries['items'][0]['id']
        if len(entries['items']) > 1:
          sys.stderr.write('duplicated file [%s/%s]\a\n' % (parent, filename))
        fileId, fileObj = self.uploadFile(path, filename, parentId, fileId)
      cn = sqlite3.connect(self.folderIds)
      cn.execute('''\
insert into folderIds (key, val, act, fol, flg) values (?, ?, ?, ?, ?);''', (
        fileId, '%s/%s' % (parent, filename), 1, 0, 0))
      cn.commit()
      cn.close()
    else:
      fileId, fileObj = self.uploadFile(path, filename, parentId, row['key'])
    return (fileId, fileObj)

  def recursiveUpload(self, remote):
    basedir = self.basedir
    b = os.path.join(basedir, remote)
    remote_id, q = self.prepare_folder(b[len(basedir):]) # set [0]='/'
    for path, dirs, files in os.walk(b):
      p_id, q = self.prepare_folder(path[len(basedir):]) # set [0]='/'
      for d in dirs:
        print 'D %s %s' % (q, d) # os.path.join(path, d)
      for f in files:
        print 'F %s %s' % (q, f) # os.path.join(path, f)
        fileId, fileObj = self.process_file(path, f, p_id, q)
        # pprint.pprint((fileId, fileObj))

class DAScript(DAClient):
  def __init__(self, basedir, folder, **kwargs):
    kwargs['script'] = True
    super(DAScript, self).__init__(basedir, **kwargs)
    self.folder = folder

  def upload(self, id, name, create=False):
    logger = logging.getLogger()
    foldername = os.path.join(self.folder, name)
    logger.info('prepare folder: %s' % foldername)
    manifest_path = os.path.join(foldername, MANIFEST)
    mfile = open(manifest_path, 'rb')
    data = simplejson.loads(mfile.read())
    mfile.close()
    # import files in the directory
    for i, fileInProject in enumerate(data['files']):
      extension = '.html' # default
      if fileInProject['type'] == 'server_js': extension = '.gs'
      filename = '%s%s' % (fileInProject['name'], extension)
      logger.info('- file%04d: %s' % (i, filename))
      f = open(os.path.join(foldername, filename), 'rb')
      fileInProject['source'] = f.read().decode('utf-8') # to unicode json
      f.close()
    # last import manifest.json
    logger.info('- manifest: %s' % MANIFEST)
    mfile = open(manifest_path, 'wb')
    mfile.write(simplejson.dumps(data))
    mfile.close()

    mbody = MediaFileUpload(manifest_path, mimetype=SCRIPT_TYPE, resumable=True)
    if create: # create new Apps Script project
      body = {'title': name, 'mimeType': SCRIPT_TYPE, 'description': name}
      fileobj = self.service.files().insert(
        body=body, media_body=mbody).execute()
      id = fileobj['id']
      # export manifest.json to refresh new file id
      download_url = fileobj['exportLinks'][SCRIPT_TYPE]
      resp, content = self.service._http.request(download_url)
      if resp.status != 200: raise Exception('An error occurred: %s' % resp)
      logger.info('- refresh: %s' % MANIFEST)
      mfile = open(manifest_path, 'wb')
      mfile.write(content) # raw string
      mfile.close()
    else: # overwrite exists Apps Script project
      body = {'mimeType': SCRIPT_TYPE}
      fileobj = self.service.files().update(
        fileId=id, body=body, media_body=mbody).execute()
    return (id, fileobj)

  def download(self, id):
    logger = logging.getLogger()
    fileobj = self.service.files().get(fileId=id).execute()
    download_url = fileobj['exportLinks'][SCRIPT_TYPE]
    resp, content = self.service._http.request(download_url)
    if resp.status != 200: raise Exception('An error occurred: %s' % resp)
    data = simplejson.loads(content)
    foldername = os.path.join(self.folder, fileobj['title'])
    logger.info('prepare folder: %s' % foldername)
    if not os.path.exists(foldername): os.makedirs(foldername)
    # Delete any files in the directory
    for the_file in os.listdir(foldername):
      file_path = os.path.join(foldername, the_file)
      try:
        if os.path.isfile(file_path): os.unlink(file_path)
      except (Exception, ), e:
        print e
    # first export manifest.json
    manifest_path = os.path.join(foldername, MANIFEST)
    logger.info('- manifest: %s' % MANIFEST)
    mfile = open(manifest_path, 'wb')
    mfile.write(content) # raw string
    mfile.close()
    # export files in the directory
    for i, fileInProject in enumerate(data['files']):
      extension = '.html' # default
      if fileInProject['type'] == 'server_js': extension = '.gs'
      filename = '%s%s' % (fileInProject['name'], extension)
      logger.info('- file%04d: %s' % (i, filename))
      f = open(os.path.join(foldername, filename), 'wb')
      f.write(fileInProject['source'].encode('utf-8')) # from unicode json
      f.close()
    return (id, None)

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

class GmailClient(AbstractClient):
  srv_name = 'gmail'
  srv_version = 'v1'

  def sendMsg(self, sender, to, subject, body, attach=None):
    '''
    select Python sample
    https://developers.google.com/gmail/api/v1/reference/users/messages/send
    SendMessage() CreateMessage() CreateMessageWithAttachment()
    '''
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage
    from email.mime.audio import MIMEAudio
    from email.mime.multipart import MIMEMultipart
    import mimetypes
    if attach is None:
      msg = MIMEText(body)
    else:
      msg = MIMEMultipart()
      mp = MIMEText(body)
      msg.attach(mp)
      fpath = os.path.join(self.basedir, attach)
      content_type, encoding = mimetypes.guess_type(fpath)
      if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
      main_type, sub_type = content_type.split('/', 1)
      mimehandlers = {'text': MIMEText, 'image': MIMEImage, 'audio': MIMEAudio}
      d = open(fpath, 'rb').read()
      if main_type in mimehandlers:
        mp = mimehandlers[main_type](d, _subtype=sub_type)
      else:
        mp = MIMEBase(main_type, sub_type)
        mp.set_payload(d)
      mp.add_header('Content-Disposition', 'attachment', filename=attach)
      msg.attach(mp)
    msg['from'] = sender
    msg['to'] = to
    msg['subject'] = subject
    mbd = {'raw': base64.b64encode(msg.as_string())}
    try:
      gmu = self.service.users()
      # userId may be set 'me' that means same as OAuth2 account.
      kwargs = {'userId': self.oa2act, 'body': mbd}
      return gmu.messages().send(**kwargs).execute()
    except (errors.HttpError, ), e:
      print e # pprint.pprint(e)

  def modifyLabels(self, msgid, addLabels=None, removeLabels=None):
    try:
      gmu = self.service.users()
      lbl = {'removeLabelIds': removeLabels if removeLabels else [],
        'addLabelIds': addLabels if addLabels else []}
      kwargs = {'userId': self.oa2act, 'id': msgid, 'body': lbl}
      return gmu.messages().modify(**kwargs).execute()
    except (errors.HttpError, ), e:
      print e # pprint.pprint(e)
