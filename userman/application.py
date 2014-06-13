" Userman: Web application root. "

import logging

import tornado
import tornado.web
import couchdb

import userman
from userman import settings
from userman import constants
from userman import utils
from userman import uimodules
from userman.requesthandler import RequestHandler

from userman.user import *
from userman.service import *
from userman.team import *
from userman.login import *
from userman.api import *


class Home(RequestHandler):
    "Home page: Form to login or link to create new account."

    def get(self):
        self.render('home.html', next=self.get_argument('next', ''))


class Version(RequestHandler):
    "Page displaying the software component versions."

    def get(self):
        "Return version information for all software in the system."
        versions = [('Userman', userman.__version__),
                    ('tornado', tornado.version),
                    ('CouchDB server', settings['DB_SERVER_VERSION']),
                    ('CouchDB module', couchdb.__version__)]
        self.render('version.html', versions=versions)


URL = tornado.web.url

handlers = \
    [URL(r'/', Home, name='home'),
     URL(r'/user/activate', UserActivate, name='user_activate'),
     URL(r'/user/reset', UserReset, name='user_reset'),
     URL(r'/user/([^/]+)', User, name='user'),
     URL(r'/user/([^/]+)/edit', UserEdit, name='user_edit'),
     URL(r'/user/([^/]+)/approve', UserApprove, name='user_approve'),
     URL(r'/user/([^/]+)/block', UserBlock, name='user_block'),
     URL(r'/user/([^/]+)/unblock', UserUnblock, name='user_unblock'),
     URL(r'/user/([^/]+)/apikey', UserApiKey, name='user_apikey'),
     URL(r'/user/([^/]+)/acknowledge',UserAcknowledge, name='user_acknowledge'),
     URL(r'/user', UserCreate, name='user_create'),
     URL(r'/users', Users, name='users'),
     URL(r'/users/pending', UsersPending, name='users_pending'),
     URL(r'/users/blocked', UsersBlocked, name='users_blocked'),
     URL(r'/service/([^/]+)', Service, name='service'),
     URL(r'/service/([^/]+)/edit', ServiceEdit, name='service_edit'),
     URL(r'/service/([^/]+)/block', ServiceBlock, name='service_block'),
     URL(r'/service/([^/]+)/unblock', ServiceUnblock, name='service_unblock'),
     URL(r'/service', ServiceCreate, name='service_create'),
     URL(r'/services', Services, name='services'),
     URL(r'/team/([^/]+)', Team, name='team'),
     URL(r'/team/([^/]+)/edit', TeamEdit, name='team_edit'),
     URL(r'/team/([^/]+)/join', TeamJoin, name='team_join'),
     URL(r'/team/([^/]+)/leave', TeamLeave, name='team_leave'),
     URL(r'/team/([^/]+)/block', TeamBlock, name='team_block'),
     URL(r'/team/([^/]+)/unblock', TeamUnblock, name='team_unblock'),
     URL(r'/team', TeamCreate, name='team_create'),
     URL(r'/teams', Teams, name='teams'),
     URL(constants.LOGIN_URL, Login, name='login'),
     URL(r'/logout', Logout, name='logout'),
     URL(r'/version', Version, name='version'),
     URL(r'/api/v1/auth/(.+)', ApiAuth, name='api_auth'),
     URL(r'/api/v1/user/(.+)', ApiUser, name='api_user'),
     URL(r'/api/v1/doc/([a-f0-9]{32})', ApiDoc, name='api_doc'),
     ]


if __name__ == "__main__":
    import sys
    import tornado.ioloop
    logging.basicConfig(level=logging.INFO)
    try:
        utils.load_settings(filepath=sys.argv[1])
    except IndexError:
        utils.load_settings()
    application = tornado.web.Application(
        handlers=handlers,
        debug=settings['TORNADO_DEBUG'],
        cookie_secret=settings['COOKIE_SECRET'],
        ui_modules=uimodules,
        template_path=constants.TEMPLATE_PATH,
        static_path=constants.STATIC_PATH,
        static_url_prefix=constants.STATIC_URL,
        login_url=constants.LOGIN_URL)
    application.listen(settings['PORT'])
    logging.info("Userman web server on port %s", settings['PORT'])
    tornado.ioloop.IOLoop.instance().start()
