#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''test_geocoding

> test_geocoding.py
Usage: test_geocoding.py [addr|lat] [lng]
(35.754560400000003, 136.0163828)
福井県敦賀市明神町１
日本, 福井県敦賀市明神町３
(35.750244299999999, 136.02107409999999)
> test_geocoding.py 京都御所
(35.025413499999999, 135.76212459999999)
> test_geocoding.py 35.025 135.762
京都府京都市上京区京都御苑３
'''

import sys, os
import googleDriveAccess as gda

def test_geocoding(geo):
  print geo.getLatLng(u'福井県敦賀市明神町')
  print geo.getLocation(35.75, 136.02)
  geo.ignoreCountryHead = False
  print geo.getLocation(*geo.getLatLng(u'福井県敦賀市明神町'))
  print geo.getLatLng(geo.getLocation(35.75, 136.02))

if __name__ == '__main__':
  geo = gda.GeocodingClient('ja', u'日本')
  sz = len(sys.argv)
  if sz < 2:
    sys.stderr.write('Usage: %s [addr|lat] [lng]\n' % sys.argv[0])
    test_geocoding(geo)
  elif sz == 2:
    import locale
    enc = locale.getpreferredencoding()
    print geo.getLatLng(sys.argv[1].decode(enc))
  elif sz >= 3:
    print geo.getLocation(sys.argv[1], sys.argv[2])
