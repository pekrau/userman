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


class ApiAuth(ApiRequestHandler):
    """Return the user information given the password and service as JSON data.
    Return only the API key for the requested service.
    Exclude all information about other services.
    Return HTTP 400 if missing parameter or invalid JSON.
    Return HTTP 401 if wrong password or service.
    Return HTTP 404 if no such user, or blocked."""

    def post(self, email):
        user = self.get_user(email, require_active=True)
        try:
            data = json.loads(self.request.body)
        except Exception, msg:
            logging.debug(str(msg))
            raise tornado.web.HTTPError(400, reason=str(msg))
        self.check_password(user, data)
        try:
            service = data['service']
        except KeyError, msg:
            raise tornado.web.HTTPError(400, reason='no service specified')
        if service not in user['services']:
            raise tornado.web.HTTPError(401, reason='service not enabled')
        user = utils.cleanup_doc(user)
        try:
            apikeys = user.pop('apikeys')
            user['apikey'] = apikeys[service]['value']
        except KeyError:
            user['apikey'] = None
        user.pop('services', None)
        self.write(user)

    def check_password(self, user, data):
        try:
            password = data['password']
        except KeyError, msg:
            raise tornado.web.HTTPError(400, reason='password missing')
        if utils.hashed_password(password) != user['password']:
            raise tornado.web.HTTPError(401, reason='invalid password')


class ApiUser(ApiAuth):
    """Return the user information given the email and service as JSON data.
    Does not need, nor checks, the password.
    Return only the API key for the requested service.
    Exclude all information about other services.
    Return HTTP 400 if missing parameter or invalid JSON.
    Return HTTP 404 if wrong service."""

    def check_password(self, user, data):
        pass
