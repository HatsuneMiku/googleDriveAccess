from setuptools import setup

long_description = open('README.md', 'rb').read()
requirements = open('requirements.txt', 'rb').read().splitlines()

setup({
  'name'            : 'googleDriveAccess',
  'version'         : '0.0.1',
  'keywords'        : 'google drive googledrive recursive upload backup import export apps script',
  'description'     : ('recursive upload to Google Drive and import-export Google Apps Script source code'),
  'long_description': long_description,
  'author'          : '999hatsune',
  'author_email'    : '999hatsune@gmail.com',
  'url'             : 'https://github.com/HatsuneMiku/googleDriveAccess',
  'download_url'    : 'https://github.com/HatsuneMiku/googleDriveAccess/tarball/0.0.1',
  'packages'        : [
    'googleDriveAccess.py',
    'encrypt_client_secret.py'
  ],
  'package_data'    : {
    '': [
      'README.md',
      'cicache.txt'
    ]
  },
  'install_requires': requirements,
  'license'         : 'BSD License',
  'classifiers'     : [
    'Development Status :: 0.0.1',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 2 :: Only'
  ]
})