from distutils.core import setup

PKG_TITLE = 'googleDriveAccess'
PKG_VER = __import__(PKG_TITLE).__version__
PKG_URL = 'https://github.com/HatsuneMiku/%s' % PKG_TITLE
PKG_KWD = '''\
google drive googledrive recursive upload backup import export apps script'''
PKG_DSC = '''\
recursive upload to Google Drive and \
import-export Google Apps Script source code'''
AUTHOR = '999hatsune'
AUTHOR_EMAIL = '999hatsune@gmail.com'
TEST_DATA = '/opt/%s' % PKG_TITLE
TEST_GAS = 'script_import_export/test_GoogleAppsScript_createCalendarEvent'

PYPI_PKGSRC = 'https://pypi.python.org/packages/source'
PYPI_DLURL = '%s/%c/%s/%s-%s.tar.gz' % (
  PYPI_PKGSRC, PKG_TITLE[0], PKG_TITLE, PKG_TITLE, PKG_VER)

long_description = open('README.md', 'rb').read()
pkg_requirements = map(lambda a: a.split('>')[0],
  open('requirements.txt', 'rb').read().splitlines())

setup(**{
  'name'            : PKG_TITLE,
  'version'         : PKG_VER,
  'keywords'        : PKG_KWD,
  'description'     : (PKG_DSC),
  'long_description': long_description,
  'author'          : AUTHOR,
  'author_email'    : AUTHOR_EMAIL,
  'url'             : PKG_URL,
  'download_url'    : PYPI_DLURL,
  'packages'        : [PKG_TITLE],
  'package_dir'     : {PKG_TITLE: './%s' % PKG_TITLE},
  'package_data'    : {
    PKG_TITLE: [
      'test/test.txt'
    ]
  },
  'data_files'      : [
    (TEST_DATA, [
      'README.md',
      'requirements.txt',
      'cicache.txt',
      'client_secret_CLIENT_ID.json.enc',
      'credentials_CLIENT_ID.json.enc',
      'encrypt_client_secret.py',
      'recursive_upload.py',
      'test_folder_create.py',
      'test_folder_hierarchy.py',
      'test_script_import_export.py',
      'test_script_prefetch.py',
      'test_upload_first.py',
      'test_upload_second.py',
      'test_document.txt'
    ]),
    ('%s/%s' % (TEST_DATA, TEST_GAS), [
      '%s/Code.gs' % TEST_GAS,
      '%s/manifest.json' % TEST_GAS
    ])
  ],
  'requires'        : pkg_requirements,
  'license'         : 'BSD License',
  'classifiers'     : [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: BSD License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 2 :: Only',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: System :: Networking',
    'Topic :: System :: Filesystems',
    'Topic :: System :: Archiving :: Mirroring',
    'Topic :: Utilities'
  ]
})