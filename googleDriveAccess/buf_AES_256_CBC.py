#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''buf_AES_256_CBC
'''

import sys, os
import random
import hashlib
from Crypto.Cipher import AES
from StringIO import StringIO
import bz2
import base64

def get_key_iv(passwd, salt):
  h = [''] * 3
  for i in range(len(h)):
    h[i] = hashlib.md5((h[i - 1] if i else '') + passwd + salt).digest()
  return h[0] + h[1], h[2]

def buf_AES_256_CBC_decrypt(inbuf, outbuf, passwd):
  if inbuf.read(8) != 'Salted__':
    raise Exception('header Salted__ is not found')
  salt = inbuf.read(8)
  key, iv = get_key_iv(passwd, salt)
  a256c = AES.new(key, AES.MODE_CBC, iv)
  dat = a256c.decrypt(inbuf.read())
  pad = ord(dat[-1])
  if 1 <= pad <= 16:
    outbuf.write(dat[:-pad])
  else:
    outbuf.write(dat)
    raise Exception('padding may be incorrect')
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

if __name__ == '__main__':
  if len(sys.argv) < 3:
    sys.stderr.write('Usage: %s pid plain\n' % sys.argv[0])
    sys.exit()
  dec = StringIO(bz2.compress(sys.argv[2]))
  enc = StringIO()
  buf_AES_256_CBC_encrypt(dec, enc, sys.argv[1])
  b = enc.read()
  enc.close()
  dec.close()
  print len(b)
  print base64.b64encode(b)
