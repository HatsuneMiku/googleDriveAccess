googleDriveAccess
=================

a Python tool to Access to the Google Drive


Sample
------

``` python

import os
import googleDriveAccess

# create instance
da = googleDriveAccess.DAClient(os.path.abspath('.'))

# create parent folders at the same time
folderId, folderPath = da.makeDirs('/remote_drive/subfolder_test/subsubfolder')
print folderId, folderPath

# recursive backup to remote folder
da.recursiveUpload('a_local_directory_you_want_to_backup_recursively')

```


How to use it
-------------

- pip install 'google-api-python-client'

- pip install googleDriveAccess

- register your App on https://console.developers.google.com/project and *'download JSON'* of your Client ID and Client secret

- rename this JSON file to './client_secret_[Client ID].json'

- create './cicache.txt' file and write your Client ID to the first line.

- execute ./encrypt_client_secret.py to encrypt downloaded JSON file

- check that encrypted file exists './client_secret_[Client ID].json.enc' and plain text JSON file './client_secret_[Client ID].json' will be deleted

- execute ./test_upload_first.py to test OAuth2 flow and store credentials

- execute ./test_upload_second.py to test OAuth2 using stored credentials

- execute ./test_script_prefetch.py to test Drive API search with query

- edit test_script_import_export.py (set 'mode = 0') to test create new Google Apps Script 'test_GoogleAppsScript_createCalendarEvent' for tests below

- execute test_script_import_export.py to test create and *'get SCRIPT_ID'*

- edit test_script_import_export.py (set 'mode = 2' and *'set SCRIPT_ID'*) to test download

- execute test_script_import_export.py to test download

- edit downloaded script './script_import_export/test_GoogleAppsScript_createCalendarEvent/Code.gs'

- edit test_script_import_export.py (set 'mode = 1') to test upload

- execute test_script_import_export.py to test upload


Known BUGs
----------

When uploading a file that would not be automaticaly handled Google Drive,
"Media type 'None' is not supported. Valid media types: [*/*]"
error occurred.
Because of default mimeType is set to None on uploadFile.
So it may correct to catch the exception and retry with 'binary/octet-stream'.


Links
-----

You can get test_*.py files at GitHub repository.
https://github.com/HatsuneMiku/googleDriveAccess

GitHub HomePage http://hatsunemiku.github.io/googleDriveAccess

PyPI https://pypi.python.org/pypi/googleDriveAccess


License
-------

BSD License

