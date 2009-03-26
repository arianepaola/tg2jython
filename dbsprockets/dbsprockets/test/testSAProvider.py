from nose.tools import raises, eq_
from dbsprockets.saprovider import SAProvider
from dbsprockets.test.testIProvider import TestIProvider
from model import *
from cgi import FieldStorage
from dbsprockets.test.base import setupDatabase, sortedTableList, teardownDatabase
from cStringIO import StringIO

def setup():
    setupDatabase()
def teardown():
    teardownDatabase()

class _TestSAProvider(TestIProvider):
    def setUp(self):
        self.provider = SAProvider(metadata)
        
    def testCreate(self):
        pass
    
    @raises(TypeError)
    def _create(self, arg1):
        SAProvider(arg1)
        
    def testCreateBad(self):
        badInput = (1, 1.2, u'a', None, (), [], {})
        for input in badInput:
            yield self._create, badInput

    def testGetTables(self):
        tables = sorted(self.provider.getTables())
        eq_(tables, sortedTableList)

    def testGetTable(self):
        table = self.provider.getTable('tg_user')
        eq_(table.name, 'tg_user')

    def testGetColumns(self):
        columns = sorted(self.provider.getColumns('tg_user'))
        eq_(columns, ['created', 'display_name', 'email_address', 'password', 'town', 'user_id', 'user_name'])

    def testGetColumn(self):
        column = self.provider.getColumn('tg_user', 'user_id')
        eq_(column.name, 'user_id')

    def testGetPrimaryKeys(self):
        keys = self.provider.getPrimaryKeys('tg_user')
        eq_(keys, ['user_id'])

    def testSelectOnPks(self):
        rows = self.provider.selectOnPks('tg_user', dict(user_id=1))
        actual = (rows[0])[:-1]
        assert list(actual) == [1, u'asdf', None, None, 'asdf', 1], "%s"%list(actual)

    def testSelectOnPksWithColumnsLimit(self):
        rows = self.provider.selectOnPks('tg_user', dict(user_id=1), columnsLimit=['user_name'])
        actual = rows[0]
        assert list(actual) == [u'asdf', ], "%s"%list(actual)

    def testSelectWithLimitAndOffset(self):
        rows = self.provider.select('tg_group', dict(user_id=1), columnsLimit=['group_name'], resultLimit=10, resultOffset=2)
        actual = rows
        assert list(actual) == [(u'2',), (u'3',), (u'4',), (u'5',), (u'6',), (u'7',), (u'8',), (u'9',), (u'10',), (u'11',)], "%s"%list(actual)

    def testSelect(self):
        rows = self.provider.select('tg_user')
        actual = (rows[0])[:-1]
        assert list(actual) == [1, u'asdf', None, None, 'asdf', 1], "%s"%list(actual)
        
    def testSelectWithColumnsLimit(self):
        rows = self.provider.select('tg_user', columnsLimit=['user_name'])
        actual = rows[0]
        assert list(actual) == [u'asdf'], "%s"%list(actual)

    def testSelectEmpty(self):
        rows = self.provider.select('tg_user', values=dict(user_name=u'asdf', user_id=0))
        assert rows == [], "%s"%rows

    def testAdd(self):
        self.provider.add('tg_user', values=dict(user_name=u'asdf2', user_id=0))
        
    def testAddWithColumnsLimit(self):
        self.provider.add('tg_user', values=dict(user_name=u'asdf4', user_id=0, enabled=True), columnsLimit=['user_name', 'user_id'])
        
    def testDelete(self):
        self.provider.add('tg_user', values=dict(user_name=u'asdf3'))
        self.provider.delete('tg_user', dict(user_id=2))

    def testEdit(self):
        self.provider.edit('tg_user', values=dict(user_id=0, user_name=u'asdf2'))
        rows = users_table.select(users_table.c.user_name==u'asdf').execute().fetchall()
        assert len(rows) == 1
        row = rows[0][:-1]
        assert row == (1, u'asdf', None, None, u'asdf', 1), "%s"%row
        
    def testGetViewColumnName(self):
        actual = self.provider.getViewColumnName('town_table')
        assert actual == 'name', actual
        
    def testGetIDColumnName(self):
        actual = self.provider.getIDColumnName('town_table')
        assert actual == 'town_id', actual
        
    def testGetForeignKeys(self):
        actual = self.provider.getForeignKeys('tg_user')
        c = users_table.columns['town']
        assert actual == [c, ], actual
        
    def testGetAssociatedManyToManyTables(self):
        actual = self.provider.getAssociatedManyToManyTables('tg_user')
        assert actual == ['tg_group', ], actual
    
    def testGetManyToManyColumns2(self):
        actual = sorted(self.provider.getManyToManyColumns('tg_group'))
        eq_(actual,  [u'permissions', u'tg_users'])

    def testGetManyToManyColumns(self):
        actual = self.provider.getManyToManyColumns('tg_user')
        eq_(actual,   [u'tg_groups'])

    def testGetManyToManyTables(self):
        actual = sorted(self.provider.getManyToManyTables())
        assert actual == ['group_permission', 'user_group'], "%s"%actual
        
    def testSetManyToMany(self):
        self.provider.setManyToMany('tg_user', 1, 'tg_group', [1,2])
        rows = user_group_table.select().execute().fetchall()
        assert rows == [(1, 1), (1, 2)], "%s"%rows

    def testSetManyToManyToo(self):
        user_group_table.delete().execute()
        self.provider.setManyToMany('tg_group', 1, 'tg_user', [1,])
        rows = user_group_table.select().execute().fetchall()
        assert rows == [(1, 1),], "%s"%rows
        
    def testSetManyToManyFailsafe(self):
        r = self.provider.setManyToMany('tg_group', 1, 'test_table', [1,])
        eq_(r, None)
    
    def testGetForeignKeyDict(self):
        d = self.provider.getForeignKeyDict('tg_user')
        assert d == {'town': {1: u'Arvada', 2: u'Denver', 3: u'Golden', 4: u'Boulder'}},  "%s"%d

    def test_findFirstColumnColumnNotFound(self):
        actual = self.provider._findFirstColumn('test_table', ['not_possible',])
        eq_(actual, 'id')
        
    def testIsUniqueNotUnique(self):
        actual = self.provider.isUnique(users_table.c.user_name, u'asdf')
        assert not actual

    def testIsUnique(self):
        actual = self.provider.isUnique(users_table.c.user_name, u'asdf_q2341234')
        assert actual
        
    def testAddFieldStorage(self):
        self.provider.add('test_table', values=dict(BLOB=FieldStorage('asdf.txt', StringIO())))
        
    def testGetDefaultValues(self):
        #we dont want to check this for reflected tables (there are no defaults set):
        if 'Reflected' in self.__class__.__name__:
            return
        actual = self.provider.getDefaultValues('test_table')
        assert sorted(actual.keys()) == ['Integer', 'created'], sorted(actual.keys())
        assert actual['Integer'] == 10
        
class TestSAProvider(_TestSAProvider):
    pass


