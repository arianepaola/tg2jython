"""
primitives Module

short cut functions for dbsprocket form creation

Classes:
Name                               Description
None

Exceptions:
None

Functions:
makeForm        make a form for user entry
makeTable       make a table for user values
makeView        view helper function
getTableValues  helper to get table values


Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
import new

from dbsprockets.saprovider import SAProvider
from dbsprockets.viewconfig import RecordViewConfig, TableViewConfig, EditableRecordViewConfig
from dbsprockets.viewfactory import ViewFactory
from dbsprockets.sessionconfig import TableViewSessionConfig
import types
from formencode.schema import Schema
from tw.forms import TableForm
import sqlalchemy
from dbsprockets.util import freshdefaults

from warnings import warn

import sqlalchemy
saVersion = int(sqlalchemy.__version__.split('.')[1])

if saVersion>4:
    from sqlalchemy.orm.attributes import ClassManager
else:
    warn('Versions of dbsprockets>=0.5 will require sqlalchemy>=0.5')

class DBHelper:
    def __init__(self):
        self._identifiers = {}
        self._metadata = None
        self._provider = None

    def getMetadata(self, model):
        raise NotImplementedError

    def getIdentifier(self, model):
        raise NotImplementedError

    def validateModel(self, model):
        raise NotImplementedError

class _SAORMDBHelper(DBHelper):

    def _firstColumn(self, model):
#        import pdb; pdb.set_trace();
        if saVersion<5 and hasattr(model, 'c'):
            warn('Versions of dbsprockets>=0.5 will require sqlalchemy>=0.5')
            return model.c[model.c.keys()[0]]
        mapper = model._sa_class_manager.mappers.values()[0]
        return mapper.c[mapper.c.keys()[0]]

    def getMetadata(self, model):
        firstColumn = self._firstColumn(model)
        if self._metadata is None:
            self._metadata = firstColumn.metadata
            self._identifiers[model] = firstColumn.table.name
        return self._metadata

    def getIdentifier(self, model):
        if model not in self._identifiers:
            self._identifiers[model] = self._firstColumn(model).table.name
        return self._identifiers[model]

    def getProvider(self, model):
        if self._provider is None:
            self._provider = SAProvider(self.getMetadata(model))
        return self._provider

    def validateModel(self, model):
        if hasattr(model, 'c') and isinstance(model.c, sqlalchemy.util.OrderedProperties):
            warn('Versions of dbsprockets>=0.5 will require sqlalchemy>=0.5')
            return

        if not hasattr(model, '_sa_class_manager') or not isinstance(model._sa_class_manager, ClassManager):
            raise TypeError('arg1(%s) has not been mapped to an sql table appropriately'%model)

        #failsafe, return a form with nothing in it
        if len(model._sa_class_manager.mappers.values()[0].c.keys()) == 0:
            raise Exception('Form has no fields')

SAORMDBHelper = _SAORMDBHelper()

#XXX:
#StormHelper = _StormHelper()
#SOHelper    = _SOHelper()

class DatabaseMixin:
    def __init__(self, dbHelper=None):
        self._dbHelper = dbHelper

    def _getHelper(self, model):
        if self._dbHelper is None:

            #sa 0.4 way of doing things
            if hasattr(model, 'c') and isinstance(model.c, sqlalchemy.util.OrderedProperties):
                warn('Versions of dbsprockets>=0.5 will require sqlalchemy>=0.5')
                self._dbHelper = SAORMDBHelper

            #use a SA Helper
            elif hasattr(model, '_sa_class_manager') and isinstance(model._sa_class_manager, ClassManager):
                self._dbHelper = SAORMDBHelper
            #other helper definitions are going in here
            else:
                raise Exception('arg1(model) has not been mapped to an sql table appropriately')
        return self._dbHelper

    def _validateModel(self, model):
        helper = self._getHelper(model)
        helper.validateModel(model)

class SprocketGenerator(DatabaseMixin):

    def makeForm(self,
                 model,
                 action,
                 identifier='',
                 controller='/',
                 hiddenFields=None,
                 disabledFields=None,
                 requiredFields=None,
                 omittedFields=None,
                 additionalFields=None,
                 limitFields=None,
                 fieldAttrs=None,
                 widgets=None,
                 validators=None,
                 formWidgetType=None,
                 formValidator=None,
                 checkIfUnique=False,
                 ):
        """
        makeForm(model,
                 action,
                 identifier='',
                 identifier='',
                 controller='/',
                 hiddenFields=[],
                 disabledFields=[],
                 requiredFields=[],
                 omittedFields=[],
                 additionalFields=[],
                 limitFields=None,
                 fieldAttrs={},
                 widgets={},
                 validators={},
                 formWidgetType=None,
                 formValidator=None
                 checkIfUnique=False)-->tw.forms.TableForm

        Generates an entry form for use in web applications.

        Arguments:
        name              type                           default    Description
        model             class                                     sqlalchemy mapped class definition
        action            String                                    string passed to the forms 'action'
        identifier        String or None                 None       optional identifier for the form
        hiddenFields      list if names                  []         fields that are hidden but not altogether
                                                                    removed from the table, useful for passing
                                                                    data through a form manually.
        disabledFields    list of names                  []         fields that are shown but not editable
        requiredFields    list of names                  []         fields that cannot be left empty by the user (validation type stuff)
        omittedFields     list of names                  []         fields that are not present, whatsoever
        additionalFields  list of Toscawidgets.fields    []         fields that you would like to add to the form that are not in the model
        limitFields       list of names                  None       limit the fields to the one in the list.  A side effect is that the
                                                                    order of the fields is set by this argument.
                                                                    (a good way to order your fields if you include all of them)
        fieldAttrs        dict of field Attrs            {}         a set of extra parameters which can be passed into the widgets
                                                                    that are created in a form.
        widgets           dict of Toscawidgets           {}         a set of widgets linked to your fields by fieldname, you must do your own validation.
        validators        dict of formencode.validators  {}         validators linked to fields in your form indexed by fieldname
        formWidgetType    ToscaWidget                    None       field for the actual widget to be used
        formValidator     Schema or validator            None       validator for the overall form
        checkIfUnique     Boolean                        False      adds default validator to "unique" fields to check if the value
                                                                    the user has entered is unique or not.
        """
        if hiddenFields is None:
            hiddenFields = []
        if disabledFields is None:
            disabledFields=[]
        if requiredFields is None:
            requiredFields=[]
        if omittedFields is None:
            omittedFields=[]
        if additionalFields is None:
            additionalFields=[]
        if fieldAttrs is None:
            fieldAttrs={}
        if widgets is None:
            widgets={}
        if validators is None:
            validators={}


        if not isinstance(action, types.StringTypes):
            raise TypeError('arg2(action) must be of type String, not %s'%type(action))
        if not isinstance(controller, types.StringTypes):
            raise TypeError('arg3(controller) must be of type String, not %s'%type(action))
        if not isinstance(identifier, types.StringTypes):
            raise TypeError('arg4(action) must be of type String, not %s'%type(action))
        if not isinstance(hiddenFields, types.ListType):
            raise TypeError('arg5(hiddenFields) must be of type List, not %s'%type(hiddenFields))
        if not isinstance(disabledFields, types.ListType):
            raise TypeError('arg6(disabledFields) must be of type List, not %s'%type(disabledFields))
        if not isinstance(omittedFields, types.ListType):
            raise TypeError('arg7(omittedFields) must be of type List, not %s'%type(omittedFields))
        if not isinstance(additionalFields, types.ListType):
            raise TypeError('arg8(additionalFields) must be of type List, not %s'%type(additionalFields))
        if limitFields is not None and not isinstance(limitFields, types.ListType):
            raise TypeError('arg9(limitFields) must be of type List, not %s'%type(limitFields))
        if not isinstance(fieldAttrs, types.DictType):
            raise TypeError('arg10(fieldAttrs) must be of type Dict, not %s'%type(limitFields))
        if not isinstance(validators, types.DictType):
            raise TypeError('arg11(validators) must be of type Dict, not %s'%type(validators))
        if formValidator is not None and not isinstance(formValidator, Schema):
            raise TypeError('arg12(formValidator) must be of type Dict, not %s'%type(formValidator))
        if not isinstance(checkIfUnique, bool):
            raise TypeError('arg13(checkIfUnique) must be of type bool, not %s'%type(checkIfUnique))

        self._validateModel(model)

        view = self.makeView(EditableRecordViewConfig,
                        model,
                        action,
                        identifier,
                        '',
                        hiddenFields,
                        disabledFields,
                        requiredFields,
                        omittedFields,
                        additionalFields,
                        limitFields,
                        fieldAttrs,
                        widgets,
                        validators,
                        formWidgetType,
                        formValidator,
                        checkIfUnique)
        return view.widget

    def makeRecordView(self,
                 model,
                 controller='',
                 omittedFields=None,
                 additionalFields=None,
                 limitFields=None,
                 fieldAttrs=None,
                 widgets=None,
                 validators=None,
                 formWidgetType=None,
                 ):
        """
        makeRecordView(model,
                 controller='',
                 omittedFields=None,
                 additionalFields=None,
                 limitFields=None,
                 fieldAttrs=None,
                 widgets=None,
                 validators=None,
                 formWidgetType=None,
                )-->Toscawidgets.TableForm

        Generates an entry form for use in web applications.

        Arguments:
        name              type                           default    Description
        model             class                                     sqlalchemy mapped class definition
        identifier        String or None                 None       optional identifier for the form
        controller        String or None                 None       helps with doing links, possibly
        omittedFields     list of names                  []         fields that are not present, whatsoever
        additionalFields  list of Toscawidgets.fields    []         fields that you would like to add to the form that are not in the model
        limitFields       list of names                  None       limit the fields to the one in the list.  A side effect is that the
                                                                    order of the fields is set by this argument.
                                                                    (a good way to order your fields if you include all of them)
        fieldAttrs        dict of field Attrs            {}         a set of extra parameters which can be passed into the widgets
                                                                    that are created in a form.
        formWidgetType    ToscaWidget                    None       field for the actual widget to be used
        """
        if omittedFields is None:
            omittedFields=[]
        if additionalFields is None:
            additionalFields=[]
        if fieldAttrs is None:
            fieldAttrs={}
        if widgets is None:
            widgets={}
        if validators is None:
            validators={}

        if not isinstance(omittedFields, types.ListType):
            raise TypeError('arg7(omittedFields) must be of type List, not %s'%type(omittedFields))
        if not isinstance(additionalFields, types.ListType):
            raise TypeError('arg8(additionalFields) must be of type List, not %s'%type(additionalFields))
        if limitFields is not None and not isinstance(limitFields, types.ListType):
            raise TypeError('arg9(limitFields) must be of type List, not %s'%type(limitFields))
        if not isinstance(fieldAttrs, types.DictType):
            raise TypeError('arg10(fieldAttrs) must be of type Dict, not %s'%type(limitFields))

        self._validateModel(model)

        view = self.makeView(RecordViewConfig,
                        model,
                        '',
                        '',
                        controller,
                        omittedFields=omittedFields,
                        additionalFields=additionalFields,
                        limitFields=limitFields,
                        fieldAttrs=fieldAttrs,
                        widgets=widgets,
                        widgetType=formWidgetType,
                         )
        return view.widget

    def makeView(self, viewConfigType,
                 model,
                 action='',
                 identifier=None,
                 controller='/',
                 hiddenFields=None,
                 disabledFields=None,
                 requiredFields=None,
                 omittedFields=None,
                 additionalFields=None,
                 limitFields=None,
                 fieldAttrs=None,
                 widgets=None,
                 validators=None,
                 widgetType=None,
                 formValidator=None,
                 checkIfUnique=False,
                 makeLinks=None
                 ):
        """this function was added so that you could cache the views more easily if you wanted to use the dbsprockets caching system"""

        if hiddenFields is None:
            hiddenFields = []
        if disabledFields is None:
            disabledFields=[]
        if requiredFields is None:
            requiredFields=[]
        if omittedFields is None:
            omittedFields=[]
        if additionalFields is None:
            additionalFields=[]
        if fieldAttrs is None:
            fieldAttrs={}
        if widgets is None:
            widgets={}
        if validators is None:
            validators={}

        helper = self._getHelper(model)
        metadata   = helper.getMetadata(model)
        identifier = helper.getIdentifier(model)
        provider   = helper.getProvider(model)

        viewConfig = viewConfigType(provider, identifier)
        viewConfig._action = action
        attrs = ['requiredFields', 'disabledFields', 'hiddenFields', 'omittedFields', 'additionalFields']
        for attr in attrs:
            tipe = eval(attr) #wouldn't be a hack unless I had a crafty eval, right?
            fields = getattr(viewConfig, attr)
            for field in tipe:
                if field not in fields:
                    fields.append(field)
        if formValidator:
            viewConfig.widgetValidator = formValidator
        if limitFields:
            viewConfig.limitFields = limitFields
        if widgetType:
            viewConfig.widgetType = widgetType
        viewConfig.checkIfUnique = checkIfUnique
        viewConfig.fieldValidators.update(validators)
        viewConfig.fieldWidgets.update(widgets)
        viewConfig.fieldAttrs.update(fieldAttrs)

        if makeLinks is not None:
            tipe = type(viewConfig)
            method = new.instancemethod(makeLinks, viewConfig, tipe)
            viewConfig._makeLinks = method

        view = ViewFactory().create(viewConfig)
        return view

    def makeTable(self, model,
                  controller=None,
                  identifier='',
                  omittedFields=None,
                  additionalFields=None,
                  limitFields=None,
                  widgetType=None,
                  makeLinks=None,
                  ):
        """
        makeTable(model,
                 controller=None,
                 identifier='',
                 omittedFields=[],
                 additionalFields=[],
                 limitFields=None,
                 widetType=None,
                 makeLinks=None,
                 )-->Toscawidgets.DataGrid

        Generates a datagrid widget for population of database data

        Arguments:
        name              type                           default    Description
        model             class                                     sqlalchemy mapped class definition
        controller        String                                    what controller to send the edit and delete links to.
        identifier        String or None                 None       optional identifier for the form
        omittedFields     list of names                  []         fields that are not present, whatsoever.
                                                                    if '_action' is in the list, then the edit/delete links will be removed.
        additionalFields  list of Toscawidgets.fields    []         fields that you would like to add to the form that are not in the model
        limitFields       list of names                  None       limit the fields to the one in the list.  A side effect is that the
                                                                    order of the fields is set by this argument.
                                                                    (a good way to order your fields if you include all of them)
        widgetType        ToscaWidget                    None       field for the parent widget to be used
        makeLinks         function                       None       Add a custom method for creating action links in your table.
        """
        if omittedFields is None:
            omittedFields=[]
        if additionalFields is None:
            additionalFields=[]

        self._validateModel(model)
        if controller is None:
            controller = ''
            omittedFields.append('_actions')

        view = self.makeView(TableViewConfig,
                        model,
                        controller=controller,
                        omittedFields=omittedFields,
                        additionalFields=additionalFields,
                        widgetType=widgetType,
                        makeLinks=makeLinks,
                        )
        return view.widget

class DataFetcher(DatabaseMixin):

    def getTableValue(self, model, offset=None, limit=None, foreignKeyFieldLabels={}):
        """
        getTableValue(model) --> SQLAlchemy result rows
        gets a set of results for a given model

        xxx: limit and offset are currently not employed

        Arguments:
        name              type                           Description
        model             class                          sqlalchemy mapped class definition
        """

        helper = self._getHelper(model)
        metadata = helper.getMetadata(model)
        identifier = helper.getIdentifier(model)
        provider = helper.getProvider(model)
        config = TableViewSessionConfig(identifier+'_session', provider, identifier=identifier)
        return config.getValue()

    def getFormDefaults(self, model):
        """
        getTableValue(model) --> SQLAlchemy result rows
        gets a set of results for a given model

        Arguments:
        name              type                           Description
        model             class                          sqlalchemy mapped class definition
        """

        helper = self._getHelper(model)
        identifier = helper.getIdentifier(model)
        provider = helper.getProvider(model)
        return provider.getDefaultValues(identifier)

generator = SprocketGenerator()
fetcher = DataFetcher()

makeForm = generator.makeForm
makeTable = generator.makeTable
makeRecordView = generator.makeRecordView
getTableValue = fetcher.getTableValue
getFormDefaults = fetcher.getFormDefaults
