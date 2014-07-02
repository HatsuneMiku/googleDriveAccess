googleDriveAccess
=================

a Python tool to Access to the Google Drive

How to use it
-------------

- register your App on https://console.developers.google.com/project and *'download JSON'* of your Client ID and Client secret

- rename this JSON file to './client_secret_[Client ID].json'

- create './cicache.txt' file and write your Client ID to the first line.

- execute ./encrypt_client_secret.py to encrypt downloaded JSON file

- check that encrypted file exists './client_secret_[Client ID].json.enc' and plain text JSON file './client_secret_[Client ID].json' will be deleted

- execute ./test_upload_first.py to test OAuth2 flow and store credentials

- execute ./test_upload_second.py to test OAuth2 using stored credentials

- execute ./test_upload_new.py to test automated scripts avobe ( first and second )

- execute ./test_script_prefetch.py to test Drive API search with query

- create directory './script_import_export' for tests below

- edit test_script_import_export.py to test download (comment #script_upload(...))

- execute test_script_import_export.py to test download

- edit downloaded script './script_import_export/[your Google Apps Script projectname]/Code.gs'

- edit test_script_import_export.py to test upload (comment #script_download(...))

- execute test_script_import_export.py to test upload

