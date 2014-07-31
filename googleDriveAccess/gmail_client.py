#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''gmail_client
'''

import sys, os
import base64
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from apiclient import errors

from abstract_client import AbstractClient

class GmailClient(AbstractClient):
  srv_name = 'gmail'
  srv_version = 'v1'

  def sendMsg(self, sender, to, subject, body, attach=None):
    '''
    select Python sample
    https://developers.google.com/gmail/api/v1/reference/users/messages/send
    SendMessage() CreateMessage() CreateMessageWithAttachment()
    '''
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

  def getMsgEntries(self, **kwargs):
    '''
    maxResults: messages count par a result separated by token
    '''
    gmu = self.service.users()
    kwargs['userId'] = self.oa2act
    return gmu.messages().list(**kwargs).execute()

  def getMsg(self, msgid, fmt=0):
    '''
    msgid: message id
    fmt: format number
    '''
    fmts = ['full', 'minimal', 'raw']
    gmu = self.service.users()
    kwargs = {'userId': self.oa2act, 'id': msgid, 'format': fmts[fmt]}
    return gmu.messages().get(**kwargs).execute()

  def getHdrsList(self, msgObj):
    return msgObj['payload']['headers']

  def getHdrsDict(self, msgObj):
    return dict(map(lambda a: (a['name'].lower(), (a['name'], a['value'])),
      self.getHdrsList(msgObj)))

  def trimWidth(self, s, m=72):
    from unicodedata import east_asian_width
    L = {'Na': 1, 'W': 2, 'F': 2, 'H': 1, 'A': 2, 'N': 1}
    u, w = [], 0
    for c in s:
      w += L[east_asian_width(c)]
      if w > m: break
      u.append(c)
    return u''.join(u)
