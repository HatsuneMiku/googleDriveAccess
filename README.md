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

``` sh

pip install 'google-api-python-client'
pip install googleDriveAccess
cd /opt/googleDriveAccess

# register your App on https://console.developers.google.com/project
# and *'download JSON'* of your Client ID and Client secret

# rename this JSON file to './client_secret_[Client ID].json'

# create './cicache.txt' file and write your Client ID to the first line.

# execute ./encrypt_client_secret.py to encrypt downloaded JSON file
./encrypt_client_secret.py

# check that encrypted file exists './client_secret_[Client ID].json.enc'
# and plain text JSON file './client_secret_[Client ID].json' will be deleted

# execute ./test_upload_first.py to test OAuth2 flow and store credentials
./test_upload_first.py

# execute ./test_upload_second.py to test OAuth2 using stored credentials
./test_upload_second.py

# execute ./test_script_prefetch.py to test Drive API search with query
./test_script_prefetch.py

# edit test_script_import_export.py (set 'mode = 0')
# to test create new Google Apps Script
# 'test_GoogleAppsScript_createCalendarEvent' for tests below

# execute ./test_script_import_export.py to test create and *'get SCRIPT_ID'*
./test_script_import_export.py

# edit test_script_import_export.py (set 'mode = 2' and *'set SCRIPT_ID'*)
# to test download

# execute ./test_script_import_export.py to test download
./test_script_import_export.py

# edit downloaded script
# './script_import_export/test_GoogleAppsScript_createCalendarEvent/Code.gs'

# edit test_script_import_export.py (set 'mode = 1') to test upload

# execute ./test_script_import_export.py to test upload
./test_script_import_export.py

```


Known BUGs
----------

I will make refresh_cache.py :

```

This program will cache each folder (or file) ids
assigned by the Google Drive (into the cache file cache_folderIds.sl3) .
Please search and erase a row that has same id from the cache file
when you delete your folder or file using another Google Drive client tool.

```


It may be fixed:

```

When uploading a file that would not be automaticaly handled Google Drive,
"Media type 'None' is not supported. Valid media types: [*/*]"
error occurred.
Because of default mimeType is set to None on uploadFile.
So it may correct to catch the exception and retry with 'binary/octet-stream'.

```


Links
-----

You can get the latest version at this GitHub repository.
https://github.com/HatsuneMiku/googleDriveAccess

GitHub HomePage http://hatsunemiku.github.io/googleDriveAccess

PyPI https://pypi.python.org/pypi/googleDriveAccess


License
-------

BSD License

