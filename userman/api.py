" Userman: API handlers. "

import logging

import tornado.web
import couchdb

from . import constants
from . import settings
from . import utils
from .requesthandler import RequestHandler


class ApiMixin(object):
    "Check API key, and redefine error method to output JSON body."

    def check_api_key(self):
        if self.get_current_user(): return
        try:
            api_key = self.request.headers['X-Userman-API-key']
        except KeyError:
            self.send_error(400, reason='API key missing')
        else:
            if api_key not in settings['API_KEYS']:
                self.send_error(400, reason='invalid API key')

    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        self.write(kwargs)


class ApiRequestHandler(ApiMixin, RequestHandler):

    def prepare(self):
        super(ApiRequestHandler, self).prepare()
        self.check_api_key()


class ApiDoc(ApiRequestHandler):
    "Return a document as is, but without '_rev' and change '_id' to 'iuid'."

    def get(self, iuid):
        try:
            self.write(utils.cleanup_doc(self.db[iuid]))
        except couchdb.http.ResourceNotFound:
            self.send_error(404, reason='no such item')


class ApiUser(ApiRequestHandler):
    """Return the user information for the email and password.
    Return only the API key for the requested service,
    and remove the service information.
    Return status 400 if missing parameter.
    Return status 404 if wrong user, password or service."""

    def get(self):
        try:
            data = dict()
            for key in ['user', 'password', 'service']:
                data[key] = self.get_argument(key)
        except tornado.web.MissingArgumentError:
            self.send_error(400, reason="missing {0}".format(key))
        else:
            try:
                user = self.get_user(data['user'])
            except tornado.web.HTTPError:
                self.send_error(404, reason='invalid user')
            else:
                if user['status'] != constants.ACTIVE:
                    self.send_error(404, reason='invalid user')
                elif data['service'] not in user['services']:
                    self.send_error(404, reason='invalid service')
                elif user['password'] != utils.hashed_password(data['password']):
                    self.send_error(404, reason='invalid password')
                else:
                    user = utils.cleanup_doc(user)
                    try:
                        apikeys = user.pop('apikeys')
                        user['apikey'] = apikeys[data['service']]['value']
                    except KeyError:
                        user['apikey'] = None
                    user.pop('services', None)
                    self.write(user)
