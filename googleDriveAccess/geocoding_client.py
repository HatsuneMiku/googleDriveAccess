#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''geocoding_client
'''

import sys, os
import urllib
import httplib2
from oauth2client.anyjson import simplejson
# import simplejson

class GeocodingClient(object):
  GEOCODING_URI = 'http://maps.google.com/maps/api/geocode/json?'

  def __init__(self, countryCode, countryStr, ignoreCountryHead=True):
    self.countryCode = countryCode
    self.countryStr = countryStr
    self.ignoreCountryHead = ignoreCountryHead
    self.init_geourl()

  def init_geourl(self):
    self.geourl = [self.GEOCODING_URI]
    self.geourl.append('sensor=false')
    self.geourl.append('&language=%s' % self.countryCode)
    self.geourl.append('&region=%s' % self.countryCode)

  def getLatLng(self, addr):
    url = self.geourl[:] # copy
    url.append('&address=%s' % urllib.quote_plus(addr.encode('utf-8')))
    http = httplib2.Http()
    headers, body = http.request(''.join(url))
    if headers.status != 200: return None
    obj = simplejson.loads(body.decode('utf-8'))
    if obj['status'] != 'OK': return None
    loc = obj['results'][0]['geometry']['location']
    return (loc['lat'], loc['lng']) # carefully drift of floating point number

  def getLocation(self, lat, lng):
    url = self.geourl[:] # copy
    url.append('&latlng=%s,%s' % (lat, lng))
    http = httplib2.Http()
    headers, body = http.request(''.join(url))
    if headers.status != 200: return None
    obj = simplejson.loads(body.decode('utf-8'))
    if obj['status'] != 'OK': return None
    for result in obj['results']:
      if 'sublocality' in result['types']:
        fa = result['formatted_address']
        if self.ignoreCountryHead:
          return fa.replace(u'%s, ' % self.countryStr, u'', 1)
        else:
          return fa
    return None
