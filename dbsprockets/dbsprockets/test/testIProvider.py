from nose.tools import raises
from dbsprockets.iprovider import IProvider

class TestIProvider:
    def setUp(self):
        self.provider = IProvider()
        
    def testCreate(self):
        pass
    
    @raises(NotImplementedError)
    def testGetTables(self):
        tables = sorted(self.provider.getTables())

    @raises(NotImplementedError)
    def testGetTable(self):
        table = self.provider.getTable('tg_user')

    @raises(NotImplementedError)
    def testGetColumns(self):
        columns = self.provider.getColumns('tg_user')

    @raises(NotImplementedError)
    def testGetColumn(self):
        column = self.provider.getColumn('tg_user', 'user_id')

    @raises(NotImplementedError)
    def testGetPrimaryKeys(self):
        keys = self.provider.getPrimaryKeys('tg_user')

    @raises(NotImplementedError)
    def testSelect(self):
        rows = self.provider.select('tg_user')
        
    @raises(NotImplementedError)
    def testAdd(self):
        self.provider.add()

    @raises(NotImplementedError)
    def testEdit(self):
        self.provider.edit()