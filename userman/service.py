" Userman: Service handlers. "

import tornado.web

from . import constants
from . import settings
from . import utils
from .saver import DocumentSaver
from .requesthandler import RequestHandler


class ServiceSaver(DocumentSaver):

    doctype = constants.SERVICE

    def initialize(self):
        self['created'] = utils.timestamp()

    def check_name(self, value):
        if '/' in value:
            raise ValueError("slash '/' disallowed in name")

    def check_status(self, value):
        if value not in [constants.ACTIVE, constants.BLOCKED]:
            raise ValueError("status not 'active' or 'blocked'")

    def convert_public(self, value):
        return utils.to_bool(value)


class Service(RequestHandler):
    "Display a service."

    def get(self, name):
        service = self.get_service(name)
        self.render('service.html',
                    service=service,
                    logs=self.get_logs(service['_id']))


class ServiceCreate(RequestHandler):
    "Create a service."

    @tornado.web.authenticated
    def get(self):
        self.check_admin()
        self.render('service_create.html')

    @tornado.web.authenticated
    def post(self):
        self.check_xsrf_cookie()
        self.check_admin()
        name = self.get_argument('name')
        try:
            self.get_service(name)
        except tornado.web.HTTPError:
            pass
        else:
            raise tornado.web.HTTPError(409, 'service already exists')
        with ServiceSaver(rqh=self) as saver:
            saver['name'] = name
            saver['description'] = self.get_argument('description', '')
            saver['href'] = self.get_argument('href', '')
            saver['status'] = self.get_argument('status', constants.BLOCKED)
            saver['public'] = self.get_argument('public', False)
        self.redirect(self.reverse_url('service', name))


class ServiceEdit(RequestHandler):
    "Edit a service."

    @tornado.web.authenticated
    def get(self, name):
        self.check_admin()
        service = self.get_service(name)
        self.render('service_edit.html', service=service)

    @tornado.web.authenticated
    def post(self, name):
        self.check_xsrf_cookie()
        self.check_admin()
        service = self.get_service(name)
        with ServiceSaver(doc=service, rqh=self) as saver:
            saver['name'] = self.get_argument('name')
            saver['description'] = self.get_argument('description', '')
            saver['href'] = self.get_argument('href', '')
            saver['status'] = self.get_argument('status', service['status'])
            saver['public'] = self.get_argument('public',
                                                service.get('public', False))
        self.redirect(self.reverse_url('service', service['name']))


class Services(RequestHandler):
    "Display all services."

    def get(self):
        self.render('services.html', services=self.get_all_services())


class ServiceBlock(RequestHandler):
    "Block a service."

    @tornado.web.authenticated
    def post(self, name):
        self.check_xsrf_cookie()
        self.check_admin()
        service = self.get_service(name)
        if service['status'] != constants.BLOCKED:
            with ServiceSaver(doc=service, rqh=self) as saver:
                saver['status'] = constants.BLOCKED
        self.redirect(self.reverse_url('service', name))


class ServiceUnblock(RequestHandler):
    "Unblock a service."

    @tornado.web.authenticated
    def post(self, name):
        self.check_xsrf_cookie()
        self.check_admin()
        service = self.get_service(name)
        if service['status'] != constants.ACTIVE:
            with ServiceSaver(doc=service, rqh=self) as saver:
                saver['status'] = constants.ACTIVE
        self.redirect(self.reverse_url('service', name))
