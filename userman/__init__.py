""" Userman: Simple account handling system for use with web services.

This implementation uses Tornado (3.2 or later) and CouchDB (1.0.1 or later).
"""

__version__ = '14.6'

import os
import socket
import yaml


def readfile(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath) as infile:
        return infile.read()
    
settings = dict(HOSTNAME=socket.gethostname().split('.')[0],
                URL_PORT=8880,
                BASE_URL='http://localhost:8880/', # XXX How def port better?
                TORNADO_DEBUG=True,
                LOGGING_DEBUG=False,
                DB_SERVER='http://localhost:5984/',
                DB_DATABASE='userman',
                API_KEYS=[],
                ACTIVATION_PERIOD=7.0, # Unit: days
                ACTIVATION_EMAIL_TEXT=readfile('messages/activation_email.txt'),
                RESET_EMAIL_TEXT=readfile('messages/reset_email.txt'),
                )

with open("{0}.yaml".format(settings['HOSTNAME'])) as infile:
    settings.update(yaml.safe_load(infile))
