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
