import unittest

class TestSQLMetadataProviderPlugin(unittest.TestCase):
    def _getTargetClass(self):
        from tg.ext.repoze.who.middleware import SQLMetadataProviderPlugin
        return SQLMetadataProviderPlugin

    def _makeOne(self, user):
        user_class = None
        user_query = UserQuery(user)
        session_factory = DummySessionFactory(user_query)
        criterion_token = 'token'
        plugin = self._getTargetClass()(user_class, session_factory,
                                        criterion_token)
                                        
        return plugin

    def test_implements(self):
        from zope.interface.verify import verifyClass
        from repoze.who.interfaces import IMetadataProvider
        klass = self._getTargetClass()
        verifyClass(IMetadataProvider, klass, tentative=True)

    def test_add_metadata_nouser(self):
        user = None
        plugin = self._makeOne(user)
        environ = {}
        identity = {'repoze.who.userid':1}
        plugin.add_metadata(environ, identity)
        self.assertEqual(identity['user'], None)
        self.assertEqual(identity['groups'], [])
        self.assertEqual(identity['permissions'], [])

    def test_add_metadata_user(self):
        user = DummyUser(True)
        plugin = self._makeOne(user)
        environ = {}
        identity = {'repoze.who.userid':1}
        plugin.add_metadata(environ, identity)
        self.assertEqual(identity['user'], user)
        self.assertEqual(identity['groups'], ['g1', 'g2'])
        self.assertEqual(identity['permissions'], ['p1', 'p2'])

class TestSQLAuthenticatorPlugin(unittest.TestCase):
    def _getTargetClass(self):
        from tg.ext.repoze.who.middleware import SQLAuthenticatorPlugin
        return SQLAuthenticatorPlugin

    def _makeOne(self, user):
        user_class = None
        user_query = UserQuery(user)
        session_factory = DummySessionFactory(user_query)
        user_id_col = 'userid'
        user_criterion = None
        plugin = self._getTargetClass()(user_class, session_factory,
                                        user_criterion, user_id_col)
        return plugin

    def _makeEnviron(self, kw=None):
        environ = {}
        environ['wsgi.version'] = (1,0)
        if kw is not None:
            environ.update(kw)
        return environ

    def test_implements(self):
        from zope.interface.verify import verifyClass
        from repoze.who.interfaces import IAuthenticator
        klass = self._getTargetClass()
        verifyClass(IAuthenticator, klass, tentative=True)

    def test_authenticate_noresults(self):
        user = None
        plugin = self._makeOne(user)
        environ = self._makeEnviron()
        identity = {'login':'foo', 'password':'bar'}
        result = plugin.authenticate(environ, identity)
        self.assertEqual(result, None)

    def test_authenticate_comparefail(self):
        user = DummyUser(False)
        plugin = self._makeOne(user)
        environ = self._makeEnviron()
        identity = {'login':'fred', 'password':'bar'}
        result = plugin.authenticate(environ, identity)
        self.assertEqual(result, None)

    def test_authenticate_comparesuccess(self):
        user = DummyUser(True)
        environ = self._makeEnviron()
        plugin = self._makeOne(user)
        identity = {'login':'fred', 'password':'bar'}
        result = plugin.authenticate(environ, identity)
        self.assertEqual(result, u'myuserid')

    def test_authenticate_nologin(self):
        user = DummyUser(True)
        environ = self._makeEnviron()
        plugin = self._makeOne(user)
        environ = self._makeEnviron()
        identity = {}
        result = plugin.authenticate(environ, identity)
        self.assertEqual(result, None)

class TestMakeWhoMiddleware(unittest.TestCase):
    def _getFUT(self):
        from tg.ext.repoze.who.middleware import make_who_middleware
        return make_who_middleware

    def test_it(self):
        # just test that it doesnt blow up
        config = {}
        app = DummyApp()
        func = self._getFUT()
        mw = func(app, config, None, None, None, None)
        self.assertEqual(mw.app, app)
        
class DummyApp:
    pass

class DummyGroup:
    def __init__(self, name):
        self.group_name = name

class DummyPermission:
    def __init__(self, name):
        self.permission_name = name
        
class DummyUser:
    userid = u'myuserid'
    groups = (DummyGroup('g1'), DummyGroup('g2'))
    permissions = (DummyPermission('p1'), DummyPermission('p2'))
    
    def __init__(self, result=True):
        self.result = result

    def validate_password(self, pwd):
        return self.result

class UserQuery:
    def __init__(self, user):
        self.user = user
    def filter(self, expr):
        return self
    def first(self):
        return self.user
    def get(self, id):
        return self.user

class DummySessionFactory:
    def __init__(self, uquery):
        self.uquery = uquery
    def __call__(self):
        return self
    def query(self, klass):
        return self.uquery
    

