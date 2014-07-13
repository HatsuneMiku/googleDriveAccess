#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''pre_convert_md_rst_html
pandoc and pyandoc
.md -> .rst -> PKG-INFO (PyPI)
         |-> filter (add css header / sourceCode -> literal-block) -> html
'''

import sys, os
from make_GitHub_doc_PyPI import md_to_html, extract_html

SRC_MD = './README.md'
DST_HTML = 'README.html'

def main():
  extract_html(DST_HTML, md_to_html(open(SRC_MD, 'rb').read()))

if __name__ == '__main__':
  main()
