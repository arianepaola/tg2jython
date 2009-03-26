from nose.tools import raises
from tw.forms.fields import *
from tw.api import Widget
from sqlalchemy import Column, Integer
from sqlalchemy.types import *
from sqlalchemy.databases.oracle import *

from dbsprockets.widgetselector import WidgetSelector, SAWidgetSelector
from dbsprockets.widgets.widgets import *
from dbsprockets.saprovider import SAProvider

class TestWidgetSelector:
    def setup(self):
        self.widgetSelector = WidgetSelector()
        
    def testCreateObj(self):
        pass
    
    def testSelect(self):
        assert self.widgetSelector.select('lala') == Widget

class DummySAWidgetSelector(SAWidgetSelector):
    defaultNameBasedWidgets = {
        'goodGollyMissMolly':     TextField,
        }
    

class TestSAWidgetSelector:
    testColumns = (
    (BLOB,        FileField),
    (BOOLEAN,     DBSprocketsCheckBox),
    (Binary,      FileField),
    (Boolean,     DBSprocketsCheckBox),
    (CHAR(100),   TextField),
    (CLOB,        TextArea),
    (DATE,        DBSprocketsCalendarDatePicker),
    (DATETIME,    DBSprocketsCalendarDateTimePicker),
    (DECIMAL,     TextField),
    (Date,        DBSprocketsCalendarDatePicker),
    (DateTime,    DBSprocketsCalendarDateTimePicker),
    (FLOAT,       TextField),
    (Float,       TextField),
    (INT,         TextField),
    (Integer,     TextField),
    (Numeric,     TextField),
    (PickleType,  TextArea),
    (SMALLINT,    TextField),
    (SmallInteger,TextField),
    (String(100),TextField),
    (TEXT,        TextArea),
    (TIME,        DBSprocketsTimePicker),
    (Time,        DBSprocketsTimePicker),
    (TIMESTAMP,   DBSprocketsCalendarDateTimePicker),
    (Unicode(100),     TextField),
    (Unicode,     TextArea),
    (VARCHAR(100),     TextField),
    (OracleNumeric,      TextField),
    (OracleDate,         DBSprocketsCalendarDatePicker),
    (OracleDateTime,     DBSprocketsCalendarDateTimePicker),
    (OracleInteger,      TextField),
    (OracleSmallInteger, TextField),

    )

    def setup(self):
        self.widgetSelector = SAWidgetSelector()
        
    def testCreateObj(self):
        pass
    
    def _testSelect(self, column, expected):
        widget = self.widgetSelector.select(column)
        assert widget == expected, "expected: %s\nactual: %s"%(expected, widget)
        
    def testSelect(self):
        for type, expected in self.testColumns:
            args={}
            if isinstance(type, Text):
                args['size'] = 100
            c = Column('asdf', type, args)
            yield self._testSelect, c, expected
            
    @raises(TypeError)
    def _select(self, arg1):
        self.widgetSelector.select(arg1)
    
    def testPasswordField(self):
        c = Column('password', String(100))
        self._testSelect(c, PasswordField)
        
    def testTextArea(self):
        c = Column('long_text', String(1000))
        self._testSelect(c, TextArea)
        
    def testSelectBad(self):
        badInput = ('a', 1, {}, [], (), None, 1.2)
        for input in badInput:
            yield self._select, input
    
    def testNameBasedWidgetSelect(self):
        c = Column('goodGollyMissMolly', Integer)
        selector = DummySAWidgetSelector()
        widget = selector.select(c)
        assert widget is TextField
