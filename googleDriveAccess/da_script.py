#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''da_script
'''

import sys, os
import logging
from apiclient.http import MediaFileUpload
from oauth2client.anyjson import simplejson
# import simplejson

from abstract_client import MANIFEST, SCRIPT_TYPE
from da_client import DAClient

class DAScript(DAClient):
  def __init__(self, basedir, folder, **kwargs):
    kwargs['script'] = True
    super(DAScript, self).__init__(basedir, **kwargs)
    self.folder = folder

  def upload(self, id, name, create=False):
    logger = logging.getLogger()
    foldername = os.path.join(self.folder, name)
    logger.info('prepare folder: %s' % foldername)
    manifest_path = os.path.join(foldername, MANIFEST)
    mfile = open(manifest_path, 'rb')
    data = simplejson.loads(mfile.read())
    mfile.close()
    # import files in the directory
    for i, fileInProject in enumerate(data['files']):
      extension = '.html' # default
      if fileInProject['type'] == 'server_js': extension = '.gs'
      filename = '%s%s' % (fileInProject['name'], extension)
      logger.info('- file%04d: %s' % (i, filename))
      f = open(os.path.join(foldername, filename), 'rb')
      fileInProject['source'] = f.read().decode('utf-8') # to unicode json
      f.close()
    # last import manifest.json
    logger.info('- manifest: %s' % MANIFEST)
    mfile = open(manifest_path, 'wb')
    mfile.write(simplejson.dumps(data))
    mfile.close()

    mbody = MediaFileUpload(manifest_path, mimetype=SCRIPT_TYPE, resumable=True)
    if create: # create new Apps Script project
      body = {'title': name, 'mimeType': SCRIPT_TYPE, 'description': name}
      fileobj = self.service.files().insert(
        body=body, media_body=mbody).execute()
      id = fileobj['id']
      # export manifest.json to refresh new file id
      download_url = fileobj['exportLinks'][SCRIPT_TYPE]
      resp, content = self.service._http.request(download_url)
      if resp.status != 200: raise Exception('An error occurred: %s' % resp)
      logger.info('- refresh: %s' % MANIFEST)
      mfile = open(manifest_path, 'wb')
      mfile.write(content) # raw string
      mfile.close()
    else: # overwrite exists Apps Script project
      body = {'mimeType': SCRIPT_TYPE}
      fileobj = self.service.files().update(
        fileId=id, body=body, media_body=mbody).execute()
    return (id, fileobj)

  def download(self, id):
    logger = logging.getLogger()
    fileobj = self.service.files().get(fileId=id).execute()
    download_url = fileobj['exportLinks'][SCRIPT_TYPE]
    resp, content = self.service._http.request(download_url)
    if resp.status != 200: raise Exception('An error occurred: %s' % resp)
    data = simplejson.loads(content)
    foldername = os.path.join(self.folder, fileobj['title'])
    logger.info('prepare folder: %s' % foldername)
    if not os.path.exists(foldername): os.makedirs(foldername)
    # Delete any files in the directory
    for the_file in os.listdir(foldername):
      file_path = os.path.join(foldername, the_file)
      try:
        if os.path.isfile(file_path): os.unlink(file_path)
      except (Exception, ), e:
        print e
    # first export manifest.json
    manifest_path = os.path.join(foldername, MANIFEST)
    logger.info('- manifest: %s' % MANIFEST)
    mfile = open(manifest_path, 'wb')
    mfile.write(content) # raw string
    mfile.close()
    # export files in the directory
    for i, fileInProject in enumerate(data['files']):
      extension = '.html' # default
      if fileInProject['type'] == 'server_js': extension = '.gs'
      filename = '%s%s' % (fileInProject['name'], extension)
      logger.info('- file%04d: %s' % (i, filename))
      f = open(os.path.join(foldername, filename), 'wb')
      f.write(fileInProject['source'].encode('utf-8')) # from unicode json
      f.close()
    return (id, None)
