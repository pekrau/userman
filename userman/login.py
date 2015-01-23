" Userman: Login and logout handlers. "

import logging

import tornado
import tornado.web

from userman import settings
from userman import constants
from userman import utils
from userman.requesthandler import RequestHandler


class Login(RequestHandler):
    "Login handler."

    def get(self):
        self.render('login.html',
                    error=None,
                    next=self.get_argument('next', None))

    def post(self):
        self.check_xsrf_cookie()
        try:
            try:
                email = self.get_argument('email')
                if not email: raise ValueError
                password = self.get_argument('password')
                if not password: raise ValueError
            except (tornado.web.MissingArgumentError, ValueError):
                raise ValueError('missing user email or password')
            try:
                user = self.get_user(email, require_active=True)
            except tornado.web.HTTPError, msg:
                raise ValueError('invalid user email')
            if user.get('password') != utils.hashed_password(password):
                changed = dict(login_failure=self.request.remote_ip)
                utils.log(self.db, user, changed=changed)
                raise ValueError('invalid password')
            self.set_secure_cookie(constants.USER_COOKIE_NAME, email)
            self._user = user
            url = self.get_argument('next', self.reverse_url('home'))
            self.redirect(url)
        except ValueError, msg:
            logging.debug("login error: %s", msg)
            self.render('login.html',
                        error=str(msg),
                        next=self.get_argument('next', None))


class Logout(RequestHandler):
    "Logout handler."

    @tornado.web.authenticated
    def post(self):
        self.check_xsrf_cookie()
        self.set_secure_cookie(constants.USER_COOKIE_NAME, '')
        self.redirect(self.reverse_url('home'))
