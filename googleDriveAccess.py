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
from oauth2client.client import OAuth2WebServerFlow, OAuth2Credentials
from oauth2client.anyjson import simplejson
# import simplejson

OAUTH_SCOPE = [
  'https://www.googleapis.com/auth/drive',
  'https://www.googleapis.com/auth/drive.scripts']

CICACHE_FILE = 'cicache.txt'
CLIENT_FILE = 'client_secret_%s.json.enc'
CREDENTIAL_FILE = 'credentials_%s.json.enc'

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

def first_authorize(basedir, clientId, script):
  print 'client secret open. CI=%s' % clientId
  pid = getpass.getpass()
  d = readJsonClient(basedir, pid, clientId)
  cli = simplejson.loads(d)['installed']
  # print cli
  scope = OAUTH_SCOPE[0] if not script else ' '.join(OAUTH_SCOPE)
  flow = OAuth2WebServerFlow(cli['client_id'], cli['client_secret'],
    scope, redirect_uri=cli['redirect_uris'][0])
  authorize_url = flow.step1_get_authorize_url()
  print 'Go to the following link in your browser: %s' % authorize_url
  code = raw_input('Enter verification code: ').strip()
  credentials = flow.step2_exchange(code)
  print 'OAuth2 success. store credential. CI=%s' % clientId
  pid = getpass2()
  store_credentials(basedir, pid, clientId, credentials)
  return credentials

def second_authorize(basedir, clientId, script=False):
  # OAuth2 and save / load credentials
  try:
    print 'OAuth2 credential open. CI=%s' % clientId
    pid = getpass.getpass()
    credentials = get_stored_credentials(basedir, pid, clientId)
    if credentials is None or credentials.invalid:
      credentials = first_authorize(basedir, clientId, script)
  except (Exception, ), e:
    credentials = first_authorize(basedir, clientId, script)

  # Connect to Google Drive
  http = credentials.authorize(httplib2.Http())
  drive_service = build('drive', 'v2', http=http)
  return drive_service
