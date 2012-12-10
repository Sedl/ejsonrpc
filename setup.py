#!/usr/bin/env python

import sys
import os
import imp


from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

sys.path.append(os.path.abspath('./src'))

VERS = imp.load_source('ejsonrcp.version.__version__', './src/ejsonrpc/version.py').__version__

add_require = []
pyvers = sys.version_info
if pyvers < (2,6):
    add_require.append('simplejson')
if pyvers < (2,7):
    add_require.append('argparse')

setup(
    name = 'ejsonrpc',
    version = VERS,
    description = 'Enhanced JSONRPC server and client',
    author = 'Stephan Sedlmeier',
    author_email = 'stephan@defectivebyte.com',
    package_dir = {'': 'src'},
    packages = find_packages('src'),
    install_requires = [
        'distribute',
        ] + add_require,
)
