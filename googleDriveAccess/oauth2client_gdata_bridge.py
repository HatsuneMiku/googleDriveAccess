#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#
# https://github.com/hnakamur/gae-oauth2client-spreadsheet
#
# The MIT License (MIT)
# Copyright (c) 2013 Hiroaki Nakamura <hnakamur@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""A bridge module between oauth2client and gdata."""

class OAuth2BearerToken(object):
  """gdata OAuth2 AuthToken using oauth2client.client.Credentials."""

  def __init__(self, credentials):
    """Initialize a token with a credentials.

    This credentials will be used later in modify_request.

    Args:
        credentials: oauth2client.client.Credentials
    """
    self.credentials = credentials

  def modify_request(self, http_request):
    """Add OAuth2 authorization header to http_request.

    Will be called from gdata.client.GDClient.request.
    This methods adds an Authorization Berer HTTP header like the following
    using self.credentials:

    "Authorization: Bearer %s" % self.credentials.access_token

    See
    http://tools.ietf.org/html/rfc6750
    https://developers.google.com/accounts/docs/OAuth2WebServer#callinganapi
    for an Authorization Bearer HTTP header.

    Args:
        http_request: atom.http_core.HttpRequest
    """
    self.credentials.apply(http_request.headers)
    return http_request
