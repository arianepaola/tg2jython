# -*- coding: utf-8 -*-

import tg, pylons
from tg.controllers import TGController
from tg.decorators import expose, validate
from routes import Mapper
from routes.middleware import RoutesMiddleware
from tg.ext.repoze.who import authorize
from nose.tools import eq_

from base import TestWSGIController, make_app, setup_session_dir, teardown_session_dir

def setup():
    setup_session_dir()
    
def _teardown():
    teardown_session_dir()
    
class SubController1(TGController):
    
    @expose()
    def index(self):
        return 'hello sub1'
    
    @expose()
    def in_group(self):
        return 'in group'

class BasicTGController(TGController):

    sub1 = SubController1()
    
    @expose()
    def index(self, **kwargs):
        return 'hello world'

    @expose()
    def default(self, remainder):
        return "Main Default Page called for url /%s"%remainder
    
    @expose()
    @authorize.require(authorize.in_group('admin'))
    def admin(self):
        return 'got to admin'
    
    @expose()
    @authorize.require(authorize.in_all_groups('reader', 'writer'))
    def all_groups(self):
        return 'got to all groups'

    @expose()
    @authorize.require(authorize.in_any_group('reader', 'writer'))
    def any_groups(self):
        return 'got to any groups'

    @expose()
    @authorize.require(authorize.is_user('asdf'))
    def asdf_user(self):
        return 'got to admin'
    
    @expose()
    @authorize.require(authorize.has_permission('write'))
    def write_perm_only(self):
        return 'got to write'
    
    @expose()
    @authorize.require(authorize.has_any_permission('read', 'write'))
    def read_perm(self):
        return 'got to read'

    @expose()
    @authorize.require(authorize.has_all_permissions('read', 'write'))
    def all_perm(self):
        return 'got to all perm'

    @expose()
    @authorize.require(authorize.not_anonymous())
    def not_anon(self):
        return 'got to not anon'
    
    @expose()
    def redirect_me(self, target, **kw):
        tg.redirect(target, kw)


class TestTGController(TestWSGIController):
    def __init__(self, *args, **kargs):
        TestWSGIController.__init__(self, *args, **kargs)
        self.app = make_app(BasicTGController)
    
    def _test_index(self):
        resp = self.app.get('/index/')
        assert 'hello' in resp.body
    
    def test_group_no_auth(self):
        resp = self.app.get('/admin')
        assert resp.body.startswith('302 Found'), resp.body
    
    def test_group_with_auth(self):
        resp = self.app.get('/login_handler?login=asdf&password=asdf')
        resp = self.app.get('/admin')
        eq_(resp.body, 'got to admin')

    def test_all_groups_no_auth(self):
        resp = self.app.get('/login_handler?login=asdf&password=asdf')
        resp = self.app.get('/all_groups')
        assert resp.body.startswith('302 Found'), resp.body
    
    def test_all_groups(self):
        resp = self.app.get('/login_handler?login=wendy&password=wendy')
        resp = self.app.get('/all_groups')
        eq_(resp.body, 'got to all groups')

    def test_any_groups_no_auth(self):
        resp = self.app.get('/login_handler?login=asdf&password=asdf')
        resp = self.app.get('/any_groups')
        assert resp.body.startswith('302 Found'), resp.body
    
    def test_any_groups(self):
        resp = self.app.get('/login_handler?login=robert&password=robert')
        resp = self.app.get('/any_groups')
        eq_(resp.body, 'got to any groups')

    def test_group_with_auth(self):
        resp = self.app.get('/login_handler?login=asdf&password=asdf')
        resp = self.app.get('/admin')
        eq_(resp.body, 'got to admin')

    def test_no_auth_not_anon(self):
        resp = self.app.get('/not_anon')
        assert resp.body.startswith('302 Found'), resp.body

    def test_not_anon(self):
        resp = self.app.get('/login_handler?login=asdf&password=asdf')
        resp = self.app.get('/not_anon')
        eq_(resp.body, 'got to not anon')

    def test_no_auth_perm(self):
        resp = self.app.get('/login_handler?login=robert&password=robert')
        resp = self.app.get('/write_perm_only')
        assert resp.body.startswith('302 Found'), resp.body

    def test_perm(self):
        resp = self.app.get('/login_handler?login=wendy&password=wendy')
        resp = self.app.get('/write_perm_only')
        eq_(resp.body, 'got to write')

    def test_no_auth_any_perm(self):
        resp = self.app.get('/login_handler?login=asdf&password=asdf')
        resp = self.app.get('/read_perm')
        assert resp.body.startswith('302 Found'), resp.body

    def test_any_perm(self):
        resp = self.app.get('/login_handler?login=wendy&password=wendy')
        resp = self.app.get('/read_perm')
        eq_(resp.body, 'got to read')

    def test_no_auth_all_perm(self):
        resp = self.app.get('/login_handler?login=asdf&password=asdf')
        resp = self.app.get('/all_perm')
        assert resp.body.startswith('302 Found'), resp.body

    def test_all_perm(self):
        resp = self.app.get('/login_handler?login=wendy&password=wendy')
        resp = self.app.get('/all_perm')
        eq_(resp.body, 'got to all perm')
        
    def test_sub_in_admin(self):
        resp = self.app.get('/login_handler?login=wendy&password=wendy')
        resp = self.app.get('/sub1/in_group')
        eq_(resp.body, 'got to all perm')
