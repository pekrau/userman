" Userman: API request handlers. "

import logging
import json

import tornado.web
import couchdb

from . import constants
from . import settings
from . import utils
from .requesthandler import RequestHandler


class ApiRequestHandler(RequestHandler):
    "Check API key unless logged in."

    def prepare(self):
        super(ApiRequestHandler, self).prepare()
        self.check_api_key()

    def check_api_key(self):
        """Check the API key given in the header.
        Return HTTP 401 if invalid or missing key."""
        if self.get_current_user(): return
        try:
            api_key = self.request.headers['X-Userman-API-key']
        except KeyError:
            self.send_error(401, reason='API key missing')
        else:
            if api_key not in settings['API_KEYS']:
                self.send_error(401, reason='invalid API key')


class ApiDoc(ApiRequestHandler):
    "Return a document as is, but without '_rev' and change '_id' to 'iuid'."

    def get(self, iuid):
        try:
            self.write(utils.cleanup_doc(self.db[iuid]))
        except couchdb.http.ResourceNotFound:
            self.send_error(404, reason='no such item')


class ApiUser(ApiRequestHandler):
    """Return the user information for the email, password and service
    given as JSON-encoded data.
    Return only the API key for the requested service,
    and remove the service information.
    Return HTTP 400 if missing parameter.
    Return HTTP 401 if wrong user, password or service."""

    def post(self):
        try:
            data = json.loads(self.request.body)
            for key in  ['user', 'password', 'service']:
                if key not in data:
                    raise KeyError("missing {0} in data".format(key))
        except Exception, msg:
            logging.debug(str(msg))
            self.send_error(400, reason=str(msg))
        else:
            try:
                user = self.get_user(data['user'])
            except tornado.web.HTTPError:
                self.send_error(401, reason='invalid user')
            else:
                if user['status'] != constants.ACTIVE:
                    self.send_error(401, reason='invalid user')
                elif data['service'] not in user['services']:
                    self.send_error(401, reason='invalid service')
                elif user['password'] != utils.hashed_password(data['password'],
                                                               check=False):
                    self.send_error(401, reason='invalid password')
                else:
                    user = utils.cleanup_doc(user)
                    try:
                        apikeys = user.pop('apikeys')
                        user['apikey'] = apikeys[data['service']]['value']
                    except KeyError:
                        user['apikey'] = None
                    user.pop('services', None)
                    self.write(user)
