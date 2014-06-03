#!/usr/bin/env python

import os
from setuptools import setup
from distutils.core import setup

os.system("pandoc -o README.txt -f markdown -t rst README.md")

setup(name='userman',
      version='14.5',
      description='Simple account handling system for use with web services.',
      author='Per Kraulis',
      author_email='per.kraulis@scilifelab.se',
      url='http://tools.scilifelab.se/',
      packages=['userman'],
      package_data={'userman': ['designs',
                                'static'
                                'templates',
                                'messages',
                                'example.yaml']},
      install_requires=['tornado',
                        'couchdb',
                        'pyyaml',
                        'pycountry',
                        'requests'],
     )
