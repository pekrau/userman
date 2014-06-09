" Userman: Context handler for saving a document. "

import tornado

from . import constants
from . import utils


class BaseSaver(object):
    """Abstract context handler creating or updating a document.
    No log entry is created on saving."""

    doctype = None

    def __init__(self, doc=None, rqh=None, db=None):
        assert self.doctype
        if rqh is not None:
            self.db = rqh.db
            self.current_user = rqh.current_user
        elif db is not None:
            self.db = db
            self.current_user = dict()
        else:
            raise ValueError('neither db nor rqh given')
        self.doc = doc or dict()
        self.changed = dict()
        self.deleted = dict()
        if '_id' in self.doc:
            assert self.doctype == self.doc[constants.DB_DOCTYPE]
        else:
            self.doc['_id'] = utils.get_iuid()
            self.doc[constants.DB_DOCTYPE] = self.doctype
            self.initialize()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        if type is not None: return False # No exceptions handled here
        self.finalize()
        self.db.save(self.doc)
        self.log()

    def __setitem__(self, key, value):
        "Update the key/value pair."
        try:
            checker = getattr(self, "check_{0}".format(key))
        except AttributeError:
            pass
        else:
            try:
                checker(value)
            except ValueError, msg:
                raise tornado.web.HTTPError(400, str(msg))
            except KeyError, msg:
                raise tornado.web.HTTPError(409, str(msg))
        try:
            converter = getattr(self, "convert_{0}".format(key))
        except AttributeError:
            pass
        else:
            value = converter(value)
        try:
            if self.doc[key] == value: return
        except KeyError:
            pass
        self.doc[key] = value
        self.changed[key] = value

    def __getitem__(self, key):
        return self.doc[key]

    def __delitem__(self, key):
        self.deleted[key] = self.doc[key]
        del self.doc[key]

    def initialize(self):
        "Perform actions when creating the document."
        pass

    def finalize(self):
        "Perform any final modifications before saving the document."
        self.doc['modified'] = utils.timestamp()

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def log(self):
        "Log save action; no action by default."
        pass


class DocumentSaver(BaseSaver):
    "Saver with log entry write on document save."

    def log(self):
        "Log document save action."
        utils.log(self.db, self.doc,
                  changed=self.changed,
                  deleted=self.deleted,
                  current_user=self.current_user)
