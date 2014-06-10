" Userman: Force change of password for an account."

import getpass

from userman import utils
from userman.user import UserSaver


def change_password(db, name):
    "Force change of password. Raise ValueError if any problem."
    doc = utils.get_user_doc(db, name)
    password = getpass.getpass('new password > ')
    with UserSaver(doc=doc, db=db) as saver:
        saver['password'] = password


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        sys.exit('give account email of username')
    try:
        change_password(utils.get_db(), sys.argv[1])
    except ValueError, msg:
        sys.exit(str(msg))
