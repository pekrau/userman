" Userman: Team handlers. "

import tornado.web

from . import constants
from . import settings
from . import utils
from .saver import DocumentSaver
from .requesthandler import RequestHandler
from .user import UserSaver


class TeamSaver(DocumentSaver):

    doctype = constants.TEAM

    def initialize(self):
        self['created'] = utils.timestamp()

    def check_name(self, value):
        if '/' in value:
            raise ValueError("slash '/' disallowed in name")

    def check_status(self, value):
        if value not in [constants.ACTIVE, constants.BLOCKED]:
            raise ValueError("status not 'active' or 'blocked'")


class TeamMixin(object):

    def get_leaders(self, team):
        return sorted([self.get_user(e) for e in team['leaders']],
                      cmp=utils.cmp_email)

    def get_members(self, team):
        return sorted([self.get_user(r.value)
                       for r in self.db.view('user/team')[team['name']]],
                      cmp=utils.cmp_email)

    def is_member(self, team, user=None):
        if user is None:
            if not self.current_user: return False
            user = self.current_user
        return team['name'] in user.get('teams', [])

    def check_member(self, team, user=None):
        if self.is_admin(): return
        if not self.is_member(team, user=user):
            raise tornado.web.HTTPError(403, 'you are not a member of team')

    def is_leader(self, team):
        return self.current_user['email'] in team['leaders']

    def check_leader(self, team):
        if self.is_admin(): return
        if not self.is_leader(team):
            raise tornado.web.HTTPError(403, 'you are not a leader of team')


class Team(TeamMixin, RequestHandler):
    "Display a team."

    @tornado.web.authenticated
    def get(self, name):
        team = self.get_team(name)
        if not team['public']:
            self.check_member(team)
        self.render('team.html',
                    team=team,
                    is_leader=self.is_leader(team),
                    is_member=self.is_member(team),
                    leaders=self.get_leaders(team),
                    members=self.get_members(team),
                    logs=self.get_logs(team['_id']))


class TeamCreate(RequestHandler):
    "Create a team."

    @tornado.web.authenticated
    def get(self):
        self.render('team_create.html')

    @tornado.web.authenticated
    def post(self):
        self.check_xsrf_cookie()
        name = self.get_argument('name')
        try:
            self.get_team(name)
        except tornado.web.HTTPError:
            pass
        else:
            raise tornado.web.HTTPError(409, 'team already exists')
        with TeamSaver(rqh=self) as saver:
            saver['name'] = name
            saver['leaders'] = [self.current_user['email']]
            saver['description'] = self.get_argument('description', '')
            saver['status'] = self.get_argument('status', constants.ACTIVE)
            saver['public'] = utils.to_bool(self.get_argument('public', False))
        with UserSaver(doc=self.current_user, rqh=self) as saver:
            saver['teams'] = sorted(saver['teams'] + [name])
        self.redirect(self.reverse_url('team', name))


class TeamEdit(TeamMixin, RequestHandler):
    "Edit a team."

    @tornado.web.authenticated
    def get(self, name):
        team = self.get_team(name)
        self.check_leader(team)
        self.render('team_edit.html',
                    team=team,
                    leaders=[u['email'] for u in self.get_leaders(team)],
                    members=[u['email'] for u in self.get_members(team)])

    @tornado.web.authenticated
    def post(self, name):
        self.check_xsrf_cookie()
        team = self.get_team(name)
        self.check_leader(team)
        with TeamSaver(doc=team, rqh=self) as saver:
            new_leaders = set()
            for email in self.get_argument('leaders').split():
                try:
                    new_leaders.add(self.get_user(email)['email'])
                except tornado.web.HTTPError:
                    pass
            saver['leaders'] = sorted(new_leaders)
            saver['description'] = self.get_argument('description', '')
            saver['status'] = self.get_argument('status', team['status'])
            saver['public'] = utils.to_bool(self.get_argument(
                    'public', team.get('public', False)))
        old_members = set([r.value for r in self.db.view('user/team')[name]])
        new_members = set()
        for email in self.get_argument('members').split():
            try:
                new_members.add(self.get_user(email)['email'])
            except tornado.web.HTTPError:
                pass
        new_members.update(new_leaders)
        for email in new_members.difference(old_members):
            user = self.get_user(email)
            if name not in user['teams']:
                with UserSaver(doc=user, rqh=self) as saver:
                    saver['teams'] = sorted(user['teams'] + [name])
        for email in old_members.difference(new_members):
            user = self.get_user(email)
            if name in user['teams']:
                with UserSaver(doc=user, rqh=self) as saver:
                    teams = set(user['teams'])
                    teams.discard(name)
                    saver['teams'] = sorted(teams)
        self.redirect(self.reverse_url('team', team['name']))


class Teams(TeamMixin, RequestHandler):
    "Display all teams."

    @tornado.web.authenticated
    def get(self):
        teams = [r.doc for r in
                 self.db.view('team/name', include_docs=True)]
        for team in teams:
            team['is_member'] = self.is_member(team)
        self.render('teams.html', teams=teams)


class TeamJoin(RequestHandler):
    "The current user joins the team."

    @tornado.web.authenticated
    def post(self, name):
        self.check_xsrf_cookie()
        user = self.get_current_user()
        if name not in user['teams']:
            team = self.get_team(name)
            if not team['public']:
                raise tornado.web.HTTPError(403, 'this is not a public team')
            with UserSaver(doc=user, rqh=self) as saver:
                saver['teams'] = sorted(user['teams'] + [name])
        self.redirect(self.reverse_url('team', name))


class TeamLeave(RequestHandler):
    "The current user leaves the team."

    @tornado.web.authenticated
    def post(self, name):
        self.check_xsrf_cookie()
        user = self.get_current_user()
        if name in user['teams']:
            team = self.get_team(name)
            with TeamSaver(doc=team, rqh=self) as saver:
                leaders = set(team['leaders'])
                leaders.discard(user['email'])
                saver['leaders'] = sorted(leaders)
                with UserSaver(doc=user, rqh=self) as saver:
                    teams = set(user['teams'])
                    teams.discard(name)
                    saver['teams'] = sorted(teams)
        self.redirect(self.reverse_url('user', user['email']))


class TeamBlock(TeamMixin, RequestHandler):
    "Block a team."

    @tornado.web.authenticated
    def post(self, name):
        self.check_xsrf_cookie()
        team = self.get_team(name)
        self.check_leader(team)
        if team['status'] != constants.BLOCKED:
            with TeamSaver(doc=team, rqh=self) as saver:
                saver['status'] = constants.BLOCKED
        self.redirect(self.reverse_url('team', name))


class TeamUnblock(TeamMixin, RequestHandler):
    "Unblock a team."

    @tornado.web.authenticated
    def post(self, name):
        self.check_xsrf_cookie()
        team = self.get_team(name)
        self.check_leader(team)
        if team['status'] != constants.ACTIVE:
            with TeamSaver(doc=team, rqh=self) as saver:
                saver['status'] = constants.ACTIVE
        self.redirect(self.reverse_url('team', name))
