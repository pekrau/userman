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
    "Check API token unless logged in."

    def prepare(self):
        super(ApiRequestHandler, self).prepare()
        self.check_api_token()

    def check_api_token(self):
        """Check the API token given in the header.
        Return HTTP 401 if invalid or missing token."""
        if self.get_current_user(): return
        try:
            api_token = self.request.headers['X-Userman-API-token']
        except KeyError:
            self.send_error(401, reason='API token missing')
        else:
            if api_token not in settings['API_TOKENS']:
                self.send_error(401, reason='invalid API token')


class ApiDoc(ApiRequestHandler):
    """Return a document as is.
    Change '_id' to 'iuid'.
    Remove '_rev' and 'password'.
    """

    def get(self, iuid):
        try:
            doc = self.db[iuid]
        except couchdb.http.ResourceNotFound:
            self.send_error(404, reason='no such item')
        else:
            # Remove sensitive or irrelevant items
            doc['iuid'] = doc.pop('_id')
            del doc['_rev']
            try:
                del doc['password']
            except KeyError:
                pass
            self.write(doc)


class ApiAuth(ApiRequestHandler):
    """Return the user information given the password and service as JSON data.
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
        # Remove sensitive or irrelevant items
        user['iuid'] = user.pop('_id')
        del user['_rev']
        del user['password']
        del user['services']
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
    NOTE: Will still check the Userman API token!
    Exclude all information about other services.
    Return HTTP 400 if missing parameter or invalid JSON.
    Return HTTP 404 if wrong service."""

    def check_password(self, user, data):
        pass
