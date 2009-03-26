from nose.tools import raises
from dbsprockets.validatorselector import ValidatorSelector, SAValidatorSelector, UniqueValue
from dbsprockets.test.base import *
from tw.forms.validators  import *
from formencode.compound import All
from sqlalchemy import Column, Integer
from sqlalchemy.databases.oracle import *
from dbsprockets.saprovider import SAProvider
from types import NoneType

def setup():
    setupDatabase()

provider = SAProvider(metadata)
class TestValidatorSelector:
    def setup(self):
        self.validatorSelector = ValidatorSelector()
        
    def testCreateObj(self):
        pass
    
    def testSelect(self):
        assert self.validatorSelector.select('lala') == UnicodeString

class TestSAValidatorSelector:
    testColumns = (
    (BLOB,        NoneType),
    (BOOLEAN,     NoneType),
    (Binary,      NoneType),
    (Boolean,     NoneType),
    (CHAR,        UnicodeString),
    (CLOB,        UnicodeString),
    (DATE,        DateValidator),
    (DATETIME,    DateValidator),
    (DECIMAL,     Number),
    (Date,        DateValidator),
    (DateTime,    DateValidator),
    (FLOAT,       Number),
    (Float,       Number),
    (INT,         Int),
    (Integer,     Int),
    (Numeric,     Number),
    (PickleType,  UnicodeString),
    (SMALLINT,    Int),
    (SmallInteger,Int),
    (String,      UnicodeString),
    (TEXT,        UnicodeString),
    (TIME,        DateValidator),
    (Time,        DateValidator),
    (TIMESTAMP,   DateValidator),
    (Unicode,     UnicodeString),
    (VARCHAR,     UnicodeString),
    (OracleNumeric,      Number),
    (OracleDate,         DateValidator),
    (OracleDateTime,     DateValidator),
    (OracleInteger,      Int),
    (OracleSmallInteger, Int),

    )

    def setup(self):
        self.validatorSelector = SAValidatorSelector(provider)
        
    def testCreateObj(self):
        pass
    
    def testSelect(self):
        for type, expected in self.testColumns:
            args={}
            if isinstance(type, Text):
                args['size'] = 100
            c = Column('asdf', type, args)
            yield self._testSelect, c, expected
            
    def _testSelect(self, column, expected):
        validator = self.validatorSelector.select(column)
        assert validator.__class__ == expected, "expected: %s\nactual: type: %s validator: %s"%(expected, column.type, validator.__type__)
        
    @raises(TypeError)
    def _select(self, arg1):
        self.validatorSelector.select(arg1)
    
    def testSelectBad(self):
        badInput = ('a', 1, {}, [], (), None, 1.2)
        for input in badInput:
            yield self._select, input
    
    def testNameBasedValidatorSelect(self):
        c = Column('email_address', String)
        validator = self.validatorSelector.select(c)
        assert isinstance(validator, Email)
        
    def testValidatorSelectorUniqueField(self):
        c = Column('nana', String, unique=True)
        validator= self.validatorSelector.select(c, checkIfUnique=True)
        assert type(validator) is All

class TestUniqueValue:
    
    def setup(self):
        self.validator = UniqueValue(SAProvider(metadata), users_table.c.user_name)
        
    @raises(Invalid)
    def testToPythonInvalid(self):
        self.validator.to_python(u'asdf', None)
        
    def testToPythonValid(self):
        self.validator.to_python(u'asdf1234', None)
