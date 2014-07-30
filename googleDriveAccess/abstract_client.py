#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''abstract_client
'''

import sys, os
import getpass
from StringIO import StringIO
import bz2
import httplib2
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow, OAuth2Credentials
from oauth2client.anyjson import simplejson
# import simplejson

from buf_AES_256_CBC import buf_AES_256_CBC_decrypt, buf_AES_256_CBC_encrypt
from . import OAUTH_SCOPE

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
