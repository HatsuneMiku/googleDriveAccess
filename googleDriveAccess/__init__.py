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

OAUTH_SCOPE = __conf__[2:]

from buf_AES_256_CBC import get_key_iv
from buf_AES_256_CBC import buf_AES_256_CBC_decrypt, buf_AES_256_CBC_encrypt
from abstract_client import readClientId, storeClientId
from abstract_client import readJsonClient, storeJsonClient
from abstract_client import readJsonCredential, storeJsonCredential, getpass2
from abstract_client import AbstractClient
from oauth2_client import OAuth2Client
from da_client import DAClient
from da_script import DAScript
from calendar_client import CalendarClient
from gmail_client import GmailClient

__all__ = ['get_key_iv', 'buf_AES_256_CBC_decrypt', 'buf_AES_256_CBC_encrypt',
  'readClientId', 'storeClientId', 'readJsonClient', 'storeJsonClient',
  'readJsonCredential', 'storeJsonCredential', 'getpass2',
  'AbstractClient', 'OAuth2Client', 'DAClient', 'DAScript',
  'CalendarClient', 'GmailClient']
