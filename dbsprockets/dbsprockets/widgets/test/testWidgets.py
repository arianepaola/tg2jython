from nose.tools import eq_
from dbsprockets.widgets.widgets import *
from dbsprockets.test.base import *
from dbsprockets.saprovider import SAProvider

setupDatabase()
provider = SAProvider(metadata)

class TestContainerWidget:
    def setup(self):
        self.widget = ContainerWidget()
        
    def testCreateObj(self):
        pass
    
    def testDisplay(self):
        s = self.widget.render()
        assert 'class="containerwidget"' in s
        
class dummy(object):
    pass
class TestFieldViewWidget:
    def setup(self):
        d = dummy
        d.name = 'key'
        self.widget = RecordFieldWidget(identifier=d)
        
    def testCreateObj(self):
        pass
    
    def testDisplay(self):
        s = self.widget.render({'key':'value'})
        eq_(s, """<tr xmlns="http://www.w3.org/1999/xhtml" class="recordfieldwidget">
    <td>
        <b>key</b>
    </td>
    <td> value
    </td>
</tr>""")
        
class TestTableViewWidget:
    def setup(self):
        self.widget = TableLabelWidget()

    def testCreateObj(self):
        pass
    
    def testDisplay(self):
        s = self.widget.render()
        assert 'class="tablelabelwidget"' in s

class TestForeignKeySingleSelectField:
    def setup(self):
        self.widget = ForeignKeySingleSelectField(tableName='tg_user', provider=provider)

    def testCreateObj(self):
        pass
    
    def testDisplay(self):
        s = self.widget.render()
        assert s == """<select xmlns="http://www.w3.org/1999/xhtml" class="foreignkeysingleselectfield">
        <option value="1">asdf</option>
</select>""", s
