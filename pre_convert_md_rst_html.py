#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''convert_md_rst_html
pandoc and pyandoc
.md -> .rst -> PKG-INFO (PyPI)
         |-> filter (add css header / sourceCode -> literal-block) -> html
'''

import sys, os
import re
import pandoc

SRC_MD = './README.md'
CSS_HEAD = 'pre/css_head.html'
DST_HTML = 'pre/README.html'
CODE_REPLACEMENTS = [
  ('sourceCode python', 'literal-block'),
  ('sourceCode bash', 'literal-block'),
  ('<pre><code>', '<pre class="literal-block"><code>')]

if os.name != 'nt':
  pandoc.core.PANDOC_PATH = 'pandoc'
else:
  if 'LOCALAPPDATA' in os.environ: app = os.getenv('LOCALAPPDATA')
  else: app = os.getenv('APPDATA')
  pandoc.core.PANDOC_PATH = '%s/Pandoc/pandoc' % (app, )

md = pandoc.Document()
md.markdown = open(SRC_MD, 'rb').read()

pd = pandoc.Document()
pd.rst = md.rst
out_html = '%s\n%s' % (open(CSS_HEAD, 'rb').read(), pd.html)

rpls = map(lambda a: (re.compile(a[0], re.M | re.S), a[1]), CODE_REPLACEMENTS)
for rpl in rpls:
  out_html = re.sub(rpl[0], rpl[1], out_html)

open(DST_HTML, 'wb').write(out_html)

dst = os.path.join(os.path.abspath('.'), DST_HTML)
if os.name != 'nt':
  import subprocess
  p = subprocess.Popen(['lynx %s' % (dst, )], 4096, None,
    None, None, None, # subprocess.PIPE, subprocess.PIPE, subprocess.PIPE
    preexec_fn=None, close_fds=False, shell=True)
  p.wait()
else:
  import win32com.client
  ie = win32com.client.Dispatch('InternetExplorer.Application')
  ie.Visible = True
  ie.Navigate(dst)
  ie.Quit()
