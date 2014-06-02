""" Userman: Initialize the database.

1) Wipeout the old database.
2) Load the design documents.
3) Create the admin user.
4) Load the dump file, if any.
"""

import os
import getpass

import couchdb

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
            saver['fullname'] = raw_input('admin full name (optional) > ')
            saver['teams'] = []
        return 'created admin user'
    else:
        return 'no password given; no new admin user created'


if __name__ == '__main__':
    response = raw_input('about to delete everything; really sure? [n] > ')
    if utils.to_bool(response):
        db = utils.get_db()
        wipeout_database(db)
        print 'wiped out database'
        load_designs(db)
        print 'loaded designs'
        default = 'dump.tar.gz'
        filename = raw_input("load data from file? [{0}] > ".format(default))
        if not filename:
            filename = default
        if os.path.exists(filename):
            count_items, count_files = undump(db, filename)
            print 'undumped', count_items, 'items and', count_files, 'files from', filename
        else:
            print 'no such file to undump'
        print create_user_admin(db)
