#!/usr/bin/env python

import os
from setuptools import setup

os.system("pandoc -o README.txt -f markdown -t rst README.md")

setup(name='userman',
      version='14.6',
      description='Simple account handling system for use with web services.',
      license='MIT',
      author='Per Kraulis',
      author_email='per.kraulis@scilifelab.se',
      url='https://github.com/pekrau/userman',
      packages=['userman'],
      include_package_data=True,
      install_requires=['tornado>=3.2',
                        'couchdb>=0.8',
                        'pyyaml>=3.10',
                        'pycountry>=1.5',
                        'requests>=2.2'],
     )
