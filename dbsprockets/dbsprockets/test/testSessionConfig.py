from nose.tools import raises, eq_
from dbsprockets.sessionconfig import *
from dbsprockets.saprovider import SAProvider
from dbsprockets.test.base import *
from dbsprockets.test.model import *
from dbsprockets.iprovider import IProvider
from cStringIO import StringIO
from cgi import FieldStorage

def setup():
    setupDatabase()

class TestSessionConfig:
    obj = SessionConfig
    provider = IProvider()
    identifier = None
    
    def setup(self):
        self.config = self.obj('', self.provider, self.identifier)

    def testCreate(self):
        pass
    
    @raises(TypeError)
    def _create(self, arg1, arg2=IProvider(), arg3=''):
        self.obj(arg1, arg2, arg3)
    
    def testCreateObjBad(self):
        badInput = ('a', (), {}, [], 1, 1.2)
        for input in badInput[1:]:
            yield self._create, input
        for input in badInput:
            yield self._create, '', input
        for input in badInput[1:]:
            yield self._create, '', self.provider, input
            
    def testValue(self):
        eq_(self.config.getValue(values={}), {})

    @raises(NotImplementedError)
    def testCount(self):
        self.config.getCount()
        
class TestDatabaseSessionConfig(TestSessionConfig):
    obj = DatabaseSessionConfig
    provider = SAProvider(metadata)
        
    def testValue(self):
        value = sorted(self.config.getValue())
        expected = sortedTableList
        assert value == expected, "expected: %s\nactual: %s"%(expected, value)
        
class TestAddRecordSessionConfig(TestSessionConfig):
    obj = AddRecordSessionConfig
    provider = SAProvider(metadata)
    identifier = 'test_table'

    def testValue(self):
        value = self.config.getValue(values={})
        expected = {'dbsprockets_id': '', 'tableName': 'test_table'}
        assert value == expected, "expected: %s\nactual: %s"%(expected, value)

class TestEditRecordSessionConfig(TestSessionConfig):
    obj = EditRecordSessionConfig
    provider = SAProvider(metadata)
    identifier = 'tg_user'

    def testValue(self):
        actual = self.config.getValue(values=dict(user_id=1))
        expected = {u'user_id': 1, 
                    'tableName': 'tg_user', 
                    u'password': u'asdf', 
                    u'user_name': u'asdf'}
        for key, value in expected.iteritems():
            assert actual[key] == value, "expected: %s\nactual: %s"%(expected, actual)
    
    def test_doGetManyToMany(self):
        config = self.obj('', self.provider, 'tg_group')
        eq_(config._doGetManyToMany(values=dict(group_id=1)), {'many_many_permission': [], 'group_id': 1, 'many_many_tg_user': []})


class TestTableViewSessionConfig(TestSessionConfig):
    obj = TableViewSessionConfig
    provider = SAProvider(metadata)
    identifier = 'tg_user'

    def testValue(self):
        actual = self.config.getValue()
        assert len(actual) == 1
        expected = {'user_id':1, 'user_name': u'asdf', 'password':u'******'}
        actual = actual[0]
        for key, value in expected.iteritems():
            assert actual[key] == value, "expected: %s\nactual: %s"%(expected, actual)

    def testValueWithFile(self):
        config = TableViewSessionConfig('id', self.provider, 'test_table',)
        actual = config.getValue()
        
    def testCount(self):
        eq_(1, self.config.getCount())


class TestTableViewSessionConfigLabel(TestSessionConfig):
    obj = TableViewSessionConfig
    provider = SAProvider(metadata)
    identifier = 'user_reference'

    def testValue(self):
        actual = self.config.getValue()[0]["user_id"]
        expected="asdf"
        assert str(actual)==expected, "expected: %s\nactual: %s"%(expected, actual)
        expected=1
        actual=actual.original
        assert actual==expected, "expected: %s\nactual: %s"%(expected, actual)
    
    def testCount(self):
        eq_(1, self.config.getCount())

