#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''test_gmail_v1
select Python sample
https://developers.google.com/gmail/api/v1/reference/users/messages/send
SendMessage() CreateMessage() CreateMessageWithAttachment()

message will be in 'SENT' label
'''

import sys, os
import time
import googleDriveAccess
from apiclient.discovery import build
from apiclient import errors
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart
import mimetypes
import base64
import pprint

def sendMsg(act, gmu, sender, to, subject, body, attach=None):
  if attach is None:
    msg = MIMEText(body)
  else:
    msg = MIMEMultipart()
    mp = MIMEText(body)
    msg.attach(mp)
    fpath = os.path.join(os.path.dirname(__file__), attach)
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
    print 'account: %s' % act
    # userId may be set 'me' that means same as OAuth2 act.
    kwargs = {'userId': act, 'body': mbd}
    mobj = gmu.messages().send(**kwargs).execute()
    pprint.pprint(mobj)
    print 'MessageId: %s - labels %s' % (mobj['id'], mobj['labelIds'])
    lbl = {'removeLabelIds': [], 'addLabelIds': ['INBOX', 'UNREAD', 'STARRED']}
    kwargs = {'userId': act, 'id': mobj['id'], 'body': lbl}
    mobj = gmu.messages().modify(**kwargs).execute()
    print 'MessageId: %s - labels %s' % (mobj['id'], mobj['labelIds'])
  except (errors.HttpError, ), e:
    pprint.pprint(e)

da = googleDriveAccess.DAClient(os.path.abspath('.'))
oauth2_service = build('oauth2', 'v2', http=da.http)
ui = oauth2_service.userinfo().get().execute()
act = ui['email']
gmail_service = build('gmail', 'v1', http=da.http)
gmu = gmail_service.users()
sendMsg(act, gmu, act, act, 'message title', 'message text')
sendMsg(act, gmu, act, act, 'title attach', 'text attach', 'test_document.txt')
