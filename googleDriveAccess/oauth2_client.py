#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''oauth2_client
'''

import sys, os

from abstract_client import AbstractClient

class OAuth2Client(AbstractClient):
  srv_name = 'oauth2'
  srv_version = 'v2'

  def userInfo(self):
    return self.service.userinfo().get().execute()
