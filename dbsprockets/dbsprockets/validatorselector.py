"""
validatorselecter Module

this contains the class which allows the ViewConfig to select the appropriate validator for the given field

Classes:
Name                               Description
ValidatorSelecter                     Parent Class
SAValidatorSelector                   Selecter Based on sqlalchemy field types
DatabaseViewValidatorSelector         Database View always selects the same validator
TableDefValidatorSelector             Table def fields use the same validator

Exceptions:
None

Functions:
None


Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
from sqlalchemy.schema import Column
from sqlalchemy.types import *
from sqlalchemy.types import String as StringType
from tw.forms.validators import *
from formencode.compound import All
from formencode import Invalid

class UniqueValue(FancyValidator):
    def __init__(self, provider, field, *args, **kw):
        self.provider = provider
        self.field    = field
        FancyValidator.__init__(self, *args, **kw)

    def _to_python(self, value, state):
        if not self.provider.isUnique(self.field, value):
            raise Invalid(
                'That value already exists',
                value, state)
        return value

class ValidatorSelector(object):
    _nameBasedValidators = {}

    def __new__(cls, *args, **kw):
        bases = cls.mro()
        chainedAttrs = ['_nameBasedValidators']
        for base in bases:
            for attr in chainedAttrs:
                if hasattr(base, attr):
                    current =  getattr(cls, attr)
                    current.update(getattr(base, attr))
        return object.__new__(cls, *args, **kw)

    def __init__(self, *args, **kw):
        pass
    
    @property
    def nameBasedValidators(self):
        validators = self._doGetNameBasedValidators()
        validators.update(self._nameBasedValidators)
        return validators

    def select(self, field, required=False, checkIfUnique=False):
        return UnicodeString

    def _doGetNameBasedValidators(self):
        return {}
    
class SAValidatorSelector(ValidatorSelector):
    
    def __init__(self, provider):
        self.provider = provider
    
    defaultValidators = {
    StringType:   UnicodeString,
    Integer:  Int,
    Numeric:  Number,
    DateTime: DateValidator,
    Date:     DateValidator,
    Time:     DateValidator,
#    Binary:   UnicodeString,
    PickleType: UnicodeString,
#    Boolean: UnicodeString,
#    NullType: TextField
    }
    _nameBasedValidators = {'email_address':Email}

    def select(self, field, required=False, checkIfUnique=False):
        if not isinstance(field, Column):
            raise TypeError("arg1 must be a sqlalchemy column, not %s"%type(field))
        
        #do not validate boolean or binary arguments
        if isinstance(field.type, (Boolean, Binary)):
            return None
        
        validatorArgs = {}
        validatorArgs['not_empty']=False
        if required:
            validatorArgs['not_empty']=True
        

        if field.name in self.nameBasedValidators:
            return self.nameBasedValidators[field.name](**validatorArgs)

        tipe = StringType
        for t in self.defaultValidators.keys():
            if isinstance(field.type, t):
                tipe = t
                break
        
        validatorType = self.defaultValidators[tipe]
        if hasattr(field.type,'length') and validatorType is UnicodeString:
            validatorArgs['max']=field.type.length
        validator = validatorType(**validatorArgs)
            
        if field.unique and checkIfUnique:
            validator = All(UniqueValue(self.provider, field), validator)
        return validator