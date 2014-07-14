#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''mkdoc
'''

import sys, os
import make_GitHub_doc_PyPI

if __name__ == '__main__':
  make_GitHub_doc_PyPI.mkdoc_main(os.path.abspath('.'))
