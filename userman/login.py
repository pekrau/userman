" Userman: Login and logout handlers. "

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
        email = self.get_argument('email', '')
        password = self.get_argument('password', '')
        if email and password:
            try:
                user = self.get_user(email, require_active=True)
            except tornado.web.HTTPError:
                pass
            else:
                password = utils.hashed_password(password)
                if user.get('password') == password:
                    self.set_secure_cookie(constants.USER_COOKIE_NAME, email)
                    url = self.get_argument('next', None)
                    if not url:
                        url = self.reverse_url('user', email)
                    self.redirect(url)
                    return
                else:
                    changed = dict(login_failure=self.request.remote_ip)
                    utils.log(self.db, user, changed=changed)
        self.render('login.html',
                    error='invalid user or password',
                    next=self.get_argument('next', None))


class Logout(RequestHandler):
    "Logout handler."

    @tornado.web.authenticated
    def post(self):
        self.check_xsrf_cookie()
        self.set_secure_cookie(constants.USER_COOKIE_NAME, '')
        self.redirect(self.reverse_url('home'))
