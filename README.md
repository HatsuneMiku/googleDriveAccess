googleDriveAccess
=================

a Python tool to Access to the Google Drive

Package Documentation https://github.com/HatsuneMiku/googleDriveAccess/wiki/module_googleDriveAccess


Sample
------

``` python
import os
import googleDriveAccess
from apiclient.discovery import build

# create instance
da = googleDriveAccess.DAClient(os.path.abspath('.'))

# create parent folders at the same time
folderId, folderPath = da.makeDirs('/remote_drive/subfolder_test/subsubfolder')
print folderId, folderPath

# recursive backup to remote folder
da.recursiveUpload('a_local_directory_you_want_to_backup_recursively')

# search
da.execQuery("explicitlyTrashed=True")
da.execQuery("'root' in parents", **{'maxResults': 5})
da.execQuery("'root' in parents and explicitlyTrashed=True", repeattoken=True, **{'maxResults': 500})

# OAuth2
oauth2_service = build('oauth2', 'v2', http=da.http)
ui = oauth2_service.userinfo().get().execute()
act = ui['email']
print act

# gmail
gmail_service = build('gmail', 'v1', http=da.http)
gmu = gmail_service.users()
sendMsg(act, gmu, act, act, 'message title', 'message text')
sendMsg(act, gmu, act, act, 'title attach', 'text attach', 'test_document.txt')
```


How to use it
-------------

Install

``` bash
pip install 'google-api-python-client'
pip install googleDriveAccess
  (or easy_install googleDriveAccess)
cd /opt/googleDriveAccess
```


First, create your Client_ID and secret on the Google Drive.

Register your App on https://console.developers.google.com/project
and *'download JSON'* of your Client ID and Client secret.

Rename this JSON file to './client_secret_[Client ID].json' .

``` bash
mv client_secrets.json /opt/googleDriveAccess/client_secret_YOURCLIENTID.json
```


Second, create cache file for Client ID .

Create './cicache.txt' file and write your Client ID to the first line.

``` bash
echo YOURCLIENTID > ./cicache.txt
```


Third, encrypt secret file.

Execute ./encrypt_client_secret.py to encrypt downloaded JSON file.

``` bash
./encrypt_client_secret.py
```


Check that encrypted file exists './client_secret_[Client ID].json.enc'
and plain text JSON file './client_secret_[Client ID].json' will be deleted.

Execute ./test_upload_first.py to test OAuth2 flow and store credentials.

``` bash
./test_upload_first.py
```


Execute ./test_upload_second.py to test OAuth2 using stored credentials.

``` bash
./test_upload_second.py
```


Execute ./test_script_prefetch.py to test Drive API search with query.

``` bash
./test_script_prefetch.py
```


Edit test_script_import_export.py (set 'mode = 0')
to test create new Google Apps Script
'test_GoogleAppsScript_createCalendarEvent' for tests below.

Execute ./test_script_import_export.py to test create and *'get SCRIPT_ID'* .

``` bash
./test_script_import_export.py
```


Edit test_script_import_export.py (set 'mode = 2' and *'set SCRIPT_ID'*)
to test download.

Execute ./test_script_import_export.py to test download.

``` bash
./test_script_import_export.py
```


Edit downloaded script
'./script_import_export/test_GoogleAppsScript_createCalendarEvent/Code.gs' .

Edit test_script_import_export.py (set 'mode = 1') to test upload.

Execute ./test_script_import_export.py to test upload.

``` bash
./test_script_import_export.py
```


Known BUGs
----------

I will make refresh_cache.py :

```
This program will cache each folder (or file) ids assigned by the Google Drive.
(Into the cache file cache_folderIds_[Client ID].sl3 .)
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

Package Documentation https://github.com/HatsuneMiku/googleDriveAccess/wiki/module_googleDriveAccess

You can get the latest version at this GitHub repository.
https://github.com/HatsuneMiku/googleDriveAccess

GitHub HomePage http://hatsunemiku.github.io/googleDriveAccess

PyPI https://pypi.python.org/pypi/googleDriveAccess


License
-------

BSD License

