""" Userman: Initialize the database, working directly towards CouchDB.

1) Wipeout the old database.
2) Load the design documents.
3) Create the admin user.
4) Load the dump file, if any.
"""

import os
import getpass

from userman import settings
from userman import constants
from userman import utils
from userman.load_designs import load_designs
from userman.user import UserSaver
from userman.dump import undump


def wipeout_database(db):
    "Wipe out the contents of the database."
    for doc in db:
        del db[doc]

def create_user_admin(db):
    "Create an admin user, if it does not already exist."
    if len(db.view('user/role')['admin']) > 0:
        return 'admin user exists'
    email = raw_input('admin email (required) > ')
    if not email:
        return 'no email given; no admin user created'
    password = getpass.getpass('admin password (required) > ')
    if password:
        with UserSaver(db=db) as saver:
            saver['email'] = email
            saver['password'] = password    # Hashing done inside saver.
            saver['role'] = constants.ADMIN
            saver['status'] = constants.ACTIVE
            saver['name'] = raw_input('admin personal name (optional) > ')
            saver['teams'] = []
        return 'created admin user'
    else:
        return 'no password given; no new admin user created'


if __name__ == '__main__':
    import sys

    # argparse only in Python 2.7 and later!
    # import argparse
    # parser = argparse.ArgumentParser(description='Initialize and load Userman database from dump file')
    # parser.add_argument('--force', action='store_true',
    #                     help='force action, rather than ask for confirmation')
    # parser.add_argument('filepath', type=str, nargs='?', default=None,
    #                     help='filepath for YAML settings file')
    # args = parser.parse_args()
    
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-f", "--force",
                      action="store_true", dest="force", default=True,
                      help='force action, rather than ask for confirmation')
    (options, args) = parser.parse_args()

    if not options.force:
        response = raw_input('about to delete everything; really sure? [n] > ')
        if not utils.to_bool(response):
            sys.exit('aborted')
    if len(args) == 0:
        filepath = None
    elif len(args) == 1:
        filepath = args[0]
    else:
        sys.exit('too many arguments')
    utils.load_settings(filepath=filepath)

    db = utils.get_db()
    wipeout_database(db)
    print 'wiped out database'
    load_designs(db)
    print 'loaded designs'
    default = 'dump.tar.gz'
    if options.force:
        filename = default
    else:
        filename = raw_input("load data from file? [{0}] > ".format(default))
        if not filename:
            filename = default
    if os.path.exists(filename):
        count_items, count_files = undump(db, filename)
        print 'undumped', count_items, 'items and', count_files, 'files from', filename
    else:
        print 'no such file to undump'
    print create_user_admin(db)
