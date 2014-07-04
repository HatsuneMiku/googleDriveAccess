#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''googleDriveAccess
Apps Script Crash Course: Import/Export Apps Script Code
https://www.youtube.com/watch?v=lEVMu9KE6jk
'''

import sys, os
import getpass
import random
import hashlib
from Crypto.Cipher import AES
from StringIO import StringIO

import httplib2
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow, OAuth2Credentials
from oauth2client.anyjson import simplejson
# import simplejson

import logging

OAUTH_SCOPE = [
  'https://www.googleapis.com/auth/drive',
  'https://www.googleapis.com/auth/drive.scripts']

CICACHE_FILE = 'cicache.txt'
CLIENT_FILE = 'client_secret_%s.json.enc'
CREDENTIAL_FILE = 'credentials_%s.json.enc'

MANIFEST = 'manifest.json'
SCRIPT_TYPE = 'application/vnd.google-apps.script+json'

def readClientId(basedir):
  f = open(os.path.join(basedir, CICACHE_FILE), 'rb')
  ci = f.readline().strip()
  f.close()
  return ci

def storeClientId(basedir, ci):
  f = open(os.path.join(basedir, CICACHE_FILE), 'wb')
  f.write(ci)
  f.close()

def get_key_iv(passwd, salt):
  h = [''] * 3
  for i in range(len(h)):
    h[i] = hashlib.md5((h[i - 1] if i else '') + passwd + salt).digest()
  return h[0] + h[1], h[2]

def buf_AES_256_CBC_decrypt(inbuf, outbuf, passwd):
  if inbuf.read(8) != 'Salted__':
    print 'header Salted__ is not found'
    return
  salt = inbuf.read(8)
  key, iv = get_key_iv(passwd, salt)
  a256c = AES.new(key, AES.MODE_CBC, iv)
  dat = a256c.decrypt(inbuf.read())
  pad = ord(dat[-1])
  if 1 <= pad <= 16:
    outbuf.write(dat[:-pad])
  else:
    outbuf.write(dat)
    print 'padding may be incorrect'
  outbuf.seek(0)

def buf_AES_256_CBC_encrypt(inbuf, outbuf, passwd):
  outbuf.write('Salted__')
  salt = ''.join(chr(random.randint(0, 0xFF)) for _ in range(8))
  outbuf.write(salt)
  key, iv = get_key_iv(passwd, salt)
  a256c = AES.new(key, AES.MODE_CBC, iv)
  dat = inbuf.read()
  pad = 16 - (len(dat) % 16) # pad should be never 0, so remove them later 1-16
  outbuf.write(a256c.encrypt(dat + (chr(pad) * pad)))
  outbuf.seek(0)

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

def readJsonCredential(basedir, pid, clientId):
  f = open(os.path.join(basedir, CREDENTIAL_FILE % clientId), 'rb')
  enc = StringIO(f.read())
  f.close()
  dec = StringIO()
  buf_AES_256_CBC_decrypt(enc, dec, pid)
  return dec.read()

def storeJsonCredential(basedir, pid, clientId, jsonStr):
  dec = StringIO(jsonStr)
  enc = StringIO()
  buf_AES_256_CBC_encrypt(dec, enc, pid)
  f = open(os.path.join(basedir, CREDENTIAL_FILE % clientId), 'wb')
  f.write(enc.read())
  f.close()

def get_stored_credentials(basedir, pid, clientId):
  return OAuth2Credentials.new_from_json(
    readJsonCredential(basedir, pid, clientId))

def store_credentials(basedir, pid, clientId, credentials):
  storeJsonCredential(basedir, pid, clientId, credentials.to_json())

def getpass2():
  pid, pid2 = None, None
  while True:
    pid = getpass.getpass()
    print 'once more'
    pid2 = getpass.getpass()
    if pid == pid2: break
    print 'both passwords are not same'
  return pid

class DAClient(object):
  def __init__(self, basedir, clientId=None, script=False, firstonly=False):
    self.basedir = basedir
    self.clientId = clientId
    self.script = script
    self.printFields = ['modifiedDate', 'title', 'id', 'mimeType']
    self.printCallback = self.defaultPrintCallback
    self.drive_service = None
    if self.clientId is None:
      self.clientId = readClientId(self.basedir)
    if not firstonly:
      if self.second_authorize() is None:
        return None

  def first_authorize(self):
    print 'client secret open. CI=%s' % self.clientId
    pid = getpass.getpass()
    d = readJsonClient(self.basedir, pid, self.clientId)
    cli = simplejson.loads(d)['installed']
    # print cli
    scope = OAUTH_SCOPE[0] if not self.script else ' '.join(OAUTH_SCOPE)
    flow = OAuth2WebServerFlow(cli['client_id'], cli['client_secret'],
      scope, redirect_uri=cli['redirect_uris'][0])
    authorize_url = flow.step1_get_authorize_url()
    print 'Go to the following link in your browser: %s' % authorize_url
    code = raw_input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    print 'OAuth2 success. store credential. CI=%s' % self.clientId
    pid = getpass2()
    store_credentials(self.basedir, pid, self.clientId, credentials)
    return credentials

  def second_authorize(self):
    # OAuth2 and save / load credentials
    try:
      print 'OAuth2 credential open. CI=%s' % self.clientId
      pid = getpass.getpass()
      credentials = get_stored_credentials(self.basedir, pid, self.clientId)
      if credentials is None or credentials.invalid:
        credentials = self.first_authorize()
    except (Exception, ), e:
      credentials = self.first_authorize()
    if credentials is None:
      return None
    # Connect to Google Drive
    http = credentials.authorize(httplib2.Http())
    self.drive_service = build('drive', 'v2', http=http)
    if self.drive_service is None:
      return None
    return self.drive_service

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
      e = self.drive_service.files().list(q=q, **kwargs).execute()
      if result is None: result = e
      else: result['items'] += e['items']
      # e does not have 'nextPageToken' key when len(e['items']) <= maxResults
      npt = e.get('nextPageToken')
      if not noprint and not self.printCallback is None: self.printCallback(e)
      if not repeattoken: break
    return result

class DAScript(DAClient):
  def __init__(self, basedir, folder, clientId=None):
    super(DAScript, self).__init__(basedir, clientId, script=True)
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
      fileobj = self.drive_service.files().insert(
        body=body, media_body=mbody).execute()
      id = fileobj['id']
      # export manifest.json to refresh new file id
      download_url = fileobj['exportLinks'][SCRIPT_TYPE]
      resp, content = self.drive_service._http.request(download_url)
      if resp.status != 200: raise Exception('An error occurred: %s' % resp)
      logger.info('- refresh: %s' % MANIFEST)
      mfile = open(manifest_path, 'wb')
      mfile.write(content) # raw string
      mfile.close()
    else: # overwrite exists Apps Script project
      body = {'mimeType': SCRIPT_TYPE}
      fileobj = self.drive_service.files().update(
        fileId=id, body=body, media_body=mbody).execute()
    return (id, fileobj)

  def download(self, id):
    logger = logging.getLogger()
    fileobj = self.drive_service.files().get(fileId=id).execute()
    download_url = fileobj['exportLinks'][SCRIPT_TYPE]
    resp, content = self.drive_service._http.request(download_url)
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
