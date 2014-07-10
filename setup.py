from distutils.core import setup
import os

try:
  import pandoc
  nopd = False
  if os.name != 'nt':
    pandoc.core.PANDOC_PATH = 'pandoc'
  else:
    if 'LOCALAPPDATA' in os.environ: app = os.getenv('LOCALAPPDATA')
    else: app = os.getenv('APPDATA')
    pandoc.core.PANDOC_PATH = '%s/Pandoc/pandoc' % (app, )
except (Exception, ), e:
  nopd = True

PKG_TITLE = 'googleDriveAccess'
mdl = __import__(PKG_TITLE)
PKG_VER = mdl.__version__
PKG_URL = mdl.__url__
AUTHOR = mdl.__author__
AUTHOR_EMAIL = mdl.__author_email__
PKG_KWD = '''\
google drive googledrive recursive upload backup import export apps script'''
PKG_DSC = '''\
recursive upload to Google Drive and \
import-export Google Apps Script source code'''

PYPI_PKGSRC = 'https://pypi.python.org/packages/source'
PYPI_DLURL = '%s/%c/%s/%s-%s.tar.gz' % (
  PYPI_PKGSRC, PKG_TITLE[0], PKG_TITLE, PKG_TITLE, PKG_VER)

long_description = open('README.md', 'rb').read()
if not nopd:
  pd = pandoc.Document()
  pd.markdown = long_description
  long_description = pd.rst

pkg_requirements = map(lambda a: a.split('>')[0],
  open('requirements.txt', 'rb').read().splitlines())

data_apdx = [
  'MANIFEST.in',
  '.gitignore',
  'README.md',
  'pre_convert_md_rst_html.py',
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
]

TEST_GAS = 'script_import_export/test_GoogleAppsScript_createCalendarEvent'
data_apdx_sub = map(lambda a: '%s/%s' % (TEST_GAS, a), [
  'Code.gs',
  'manifest.json'
])

if os.name != 'nt':
  apdx_dir = '/opt/%s' % (PKG_TITLE, ) # setup as data_files
  pkg_apdx = []
else: # to avlid SandboxViolation on mkdir
  apdx_dir = 'conf/%s' % (PKG_TITLE, ) # setup as package_data
  #pkg_apdx = map(lambda a: '%s/%s' % (apdx_dir, a), data_apdx + data_apdx_sub)
  pkg_apdx = []

package_data = {
  PKG_TITLE: [
    'conf/setup.cf'
  ] + pkg_apdx
}

kwargs = {
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
  'package_data'    : package_data,
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
}

if os.name != 'nt':
  kwargs['data_files'] = [
    (apdx_dir, data_apdx),
    ('%s/%s' % (apdx_dir, TEST_GAS), data_apdx_sub)
  ]

setup(**kwargs)