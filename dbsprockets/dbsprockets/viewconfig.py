"""
ViewConfig Module

The ViewConfig defines all of the View related issues for dbsprockets

Classes:
Name                               Description
ViewConfig                         Parent Class
DatabaseViewConfig
EditRecordConfig
TableDefViewConfig
TableViewConfig
AddRecordViewConfig

Exceptions:
None

Functions:
None

Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
import types
from cStringIO import StringIO
from tw.forms.fields import HiddenField
from tw.api import Widget
from tw.forms import DataGrid, TableForm, SingleSelectField, TextField
from copy import copy
from urllib import quote
from genshi.input import HTML, XML 

from dbsprockets.validatorselector import ValidatorSelector, SAValidatorSelector
from dbsprockets.widgetselector import *
from dbsprockets.widgets.widgets import *
from dbsprockets.metadata import *
from dbsprockets.iprovider import IProvider
from tw.forms.validators import String,Int
from formencode.compound import All
from formencode import Schema

class FilteringSchema(Schema):
    filter_extra_fields = True
    allow_extra_fields = True

from tw.forms.fields import SingleSelectField

class ViewConfigMeta(object):
    _hiddenFields     = []
    _disabledFields   = []
    _requiredFields   = []
    _omittedFields    = []
    _additionalFields = []
    
    limitFields = None

    validatorSelectorType = ValidatorSelector
    widgetValidator  = None
    checkIfUnique  = False

    _fieldWidgets     = {}
    _fieldAttrs       = {}
    _fieldValidators  = {}

    widgetType = Widget
    widgetSelectorType = WidgetSelector

    metadataType = Metadata

    def __new__(cls, *args, **kw):
        bases = cls.mro()
        chainedAttrs = ['_hiddenFields', '_requiredFields', '_disabledFields', '_omittedFields']
        for base in bases:
            for attr in chainedAttrs:
                if hasattr(base, attr):
                    current =  getattr(cls, attr)
                    setattr(cls, attr, current + [item for item in getattr(base, attr) if item not in current])
        return object.__new__(cls, *args, **kw)

    def __init__(self, provider, identifier=None, controller='/'):
        """(metadata, controller)"""
        if not isinstance(provider, IProvider):
            raise TypeError('arg1 should be an IProvider, not a : %s', type(provider))
        if not isinstance(identifier, types.StringTypes):
            raise TypeError('arg2 should be a String, not a: %s', type(identifier))
        if not isinstance(controller, types.StringTypes):
            raise TypeError('arg3 should be a String,  not a: %s', type(controller))
        
        self.provider = provider
        self.identifier = identifier
        self.controller = controller
        self.metadata = self.metadataType(provider, identifier)
        self.widgetSelector = self._doGetWidgetSelector()
        self.validatorSelector = self.validatorSelectorType(provider)
        
        self.__hiddenFields     = copy(self._hiddenFields)
        self.__disabledFields   = copy(self._disabledFields)
        self.__requiredFields   = copy(self._requiredFields)
        self.__omittedFields    = copy(self._omittedFields)
        self.__additionalFields = copy(self._additionalFields)
     
        self.fieldWidgets       = copy(self._fieldWidgets)
        self.fieldAttrs         = copy(self._fieldAttrs)
        self.fieldValidators    = copy(self._fieldValidators)

    def _getOmittedFields(self):
        return self.__omittedFields
    def _setOmittedFields(self, item):
        self.__omittedFields = item
    omittedFields = property(_getOmittedFields, _setOmittedFields)

    def _getAdditionalFields(self):
        return self.__additionalFields
    def _setAdditionalFields(self, item):
        self.__additionalFields = item
    additionalFields = property(_getAdditionalFields, _setAdditionalFields)

    def _getDisabledFields(self):
        fields =  self.__disabledFields
        fields.extend([field for field in self._doGetDisabledFields() if field not in fields])
        return fields
    def _setDisabledFields(self, item):
        self.__disabledFields = item
    disabledFields = property(_getDisabledFields, _setDisabledFields)

    def _getRequiredFields(self):
        return self.__requiredFields
    def _setRequiredFields(self, item):
        self.__requiredFields = item
    requiredFields = property(_getRequiredFields, _setRequiredFields)

    def _getHiddenFields(self):
        return self.__hiddenFields
    def _setHiddenFields(self, item):
        self.__hiddenFields = item
    hiddenFields = property(_getHiddenFields, _setHiddenFields)

    @property
    def manytoManyFields(self):
        return self._doGetManyToManyFields()

    @property
    def fields(self):
        if self.limitFields is not None:
            return self.limitFields
        return self.metadata.keys()

    def _createHiddenFields(self):
        fields = []
        idField = HiddenField(id='dbsprockets_id')
        fields.extend([HiddenField(id=field, identifier=field) for field in self.hiddenFields if field not in self.omittedFields]  )
        fields.extend([HiddenField(id=field, identifier=field) for field in self.disabledFields if field not in self.omittedFields and field not in self.hiddenFields])
        fields.append(idField)
        return fields
    
    def getWidgetArgs(self, id=None):
        fieldAttrs = self.fieldAttrs
        hiddenFields = self.hiddenFields
        disabledFields = self.disabledFields
        requiredFields = self.requiredFields
        omittedFields = self.omittedFields
        validators = self.fieldValidators
        fieldWidgets = self.fieldWidgets
        fields = self.fields
        manyToManyFields = self.manytoManyFields

        children = []
        for fieldName in fields:
            if fieldName in fieldWidgets:
                children.append(fieldWidgets[fieldName])
                continue
            if fieldName in omittedFields:
                continue
            if fieldName in manyToManyFields:
                continue
            
            field = self.metadata[fieldName]
            widgetType = self.widgetSelector.select(field)
            childWidgetArgs = self._doGetChildWidgetArgsForWidgetType(field, widgetType)
            childWidgetArgs.update({'id':fieldName, 'identifier':field})
            
            required = fieldName in requiredFields
            disabled = fieldName in disabledFields
            hidden   = fieldName in hiddenFields
            checkIfUnique = self.checkIfUnique

            validator = None
            if not disabled:
                if fieldName in validators:
                    validator = validators[fieldName]
                else:
                    validator = self.validatorSelector.select(field, required, checkIfUnique)
            if validator != None:
                childWidgetArgs['validator'] = validator

            if fieldName in disabledFields:
                childWidgetArgs['disabled'] = True
                childWidgetArgs['id'] = fieldName
                childWidgetArgs['validator'] = String(if_missing=None)

            if fieldName in fieldAttrs:
                childWidgetArgs['attrs'] = fieldAttrs[fieldName]
                
            children.append(widgetType(**childWidgetArgs))
        children.extend(self._createHiddenFields())
        children.extend(self._doGetManyToManyWidgets(manyToManyFields))
        children.extend(self.additionalFields)
        d = dict(children=children)
        d['controller'] = self.controller
        if self.widgetValidator:
            d['validator'] = self.widgetValidator
        else:
            d['validator'] = FilteringSchema
        d.update(self._doAddExtraWidgetArgs())
        return d

    @property
    def action(self):
        return self._doGetAction()
    
    def _doGetManyToManyFields(self):
        return []
    def _doGetAction(self):
        raise NotImplementedError
    def _doAddExtraWidgetArgs(self):
        return {}
    def _doGetWidgetSelector(self):
        return self.widgetSelectorType()
    def _doGetChildWidgetArgsForWidgetType(self, field, widgetType):
        return {}
    def _doGetManyToManyWidgets(self, fields):
        return []
    def _doGetDisabledFields(self):
        return []
    
class ViewConfig(ViewConfigMeta):pass

class DatabaseViewConfig(ViewConfig):
    widgetType = ContainerWidget
    metadataType = DatabaseMetadata
    widgetSelectorType = DatabaseViewWidgetSelector

class TableDefViewConfig(ViewConfig):
    widgetType = TableWidget
    metadataType = FieldsMetadata
    widgetSelectorType = TableDefWidgetSelector

class RecordViewConfig(ViewConfig):
    widgetType = RecordViewWidget
    metadataType = FieldsMetadata
    widgetSelectorType = RecordViewWidgetSelector

class TableViewConfig(ViewConfig):
    widgetType = DataGrid
    metadataType = FieldsMetadata
    foreignKeyFieldLabels = ['name', '_name', 'description', '_description', 'title']

    def _writePKsToURL(self, pks, row):
        stream = StringIO()
        l = len(pks) - 1
        for i, pk in enumerate(pks):
            if i == 0:
                stream.write('?')
            else:
                stream.write('&')
            stream.write(str(pk))
            stream.write('=')
            value=row[pk]
            if hasattr(value,"original"):
                value=value.original
            if isinstance(value, unicode):
                value=value.encode('utf8')
            value=quote(str(value))
            stream.write(value)
        
        return stream.getvalue()
    
    def _makeLinks(self, row):
        pks = self.metadata.primaryKeys()
        editLink = StringIO()
        editLink.write('<a href="')
        editLink.write(self.controller+'/editRecord/')
        editLink.write(self.metadata.identifier)
        editLink.write(self._writePKsToURL(pks, row))
        editLink.write('">edit</a>')

        deleteLink = StringIO()
        deleteLink.write('<a href="')
        deleteLink.write(self.controller+'/delete/')
        deleteLink.write(self.metadata.identifier)
        deleteLink.write(self._writePKsToURL(pks, row))
        deleteLink.write('">delete</a>')
        editLink.write('|')
        editLink.write(deleteLink.getvalue())
        return HTML(editLink.getvalue())

    def getWidgetArgs(self):
        fields = self.fields
        pks  = self.metadata.primaryKeys()
        omittedFields = self.omittedFields
        fields = [(field, eval('lambda d: d["'+field+'"]')) for field in fields if field not in omittedFields]
        if '_actions' not in omittedFields:
            fields.insert(0, (' ', self._makeLinks))
        manyToManyTables = self.provider.getManyToManyTables()
        if self.identifier not in manyToManyTables:
            manyToManyColumns = self.provider.getManyToManyColumns(self.identifier)
            fields.extend([('%s'%table, eval('lambda d: d["'+table+'"]')) for table in manyToManyColumns])
        return dict(id=self.__class__.__name__, fields=fields)
        
class EditableRecordViewConfig(ViewConfig):
    widgetType = DBSprocketsTableForm
    metadataType = FieldsMetadata
    widgetSelectorType = SAWidgetSelector
    validatorSelectorType = SAValidatorSelector
    _hiddenFields     = ['tableName']
    _action = ''
    def _doGetAction(self):
        return self._action

    def _doAddExtraWidgetArgs(self):
        return dict(action=self.action)

    def _doGetDisabledFields(self):
        return self.metadata.primaryKeys()
    
    def _doGetManyToManyFields(self):
        associatedTables = self.provider.getAssociatedManyToManyTables(self.identifier)
        return [table+'s' for table in associatedTables]
    
    def _doGetManyToManyWidgets(self, fields):
        tableName = self.identifier
        widgets = []
        omittedFields = self.omittedFields
        hiddenFields  = self.hiddenFields
        limitFields   = self.limitFields
        for fieldName in fields:
            table = fieldName[:-1]
            if not (fieldName in hiddenFields ) and \
               not (fieldName in omittedFields) and \
                   ((limitFields is None) or (fieldName in limitFields)):
                        widgets.append(ForeignKeyMultipleSelectField(id="many_many_"+table, label_text=fieldName, tableName=table, provider=self.provider))
        return widgets
    
    def _doGetChildWidgetArgsForWidgetType(self, field, widgetType):
        if widgetType == ForeignKeySingleSelectField:
            nullable=self.provider.isNullableField(field)
            return dict(nullable=nullable, validator=String(if_missing=None), provider=self.provider, tableName=field.foreign_keys[0].column.table.name)
        if widgetType==TextField and hasattr(field.type, 'length') and (not field.type.length is None):
            maxlength=field.type.length
            if field.type.length>80:
                size=80
            else:
                size=field.type.length
            return dict(size=size,maxlength=maxlength)
        return {}

class EditRecordViewConfig(EditableRecordViewConfig):
    widgetType = DBSprocketsTableForm
    metadataType = FieldsMetadata
    widgetSelectorType = SAWidgetSelector
    validatorSelectorType = SAValidatorSelector
    _hiddenFields     = ['tableName']
    
    def _doGetAction(self):
        return self.controller+'/edit'

class AddRecordViewConfig(EditRecordViewConfig):
    checkIfUnique = True
    def _doGetAction(self):
        return self.controller+'/add'

    def _doGetDisabledFields(self):
        foreignKeys=self.metadata.foreignKeys
        return [k for k in self.metadata.primaryKeys() if k in self.metadata.autoIncrementFields and not k in foreignKeys]