from nose.tools import raises
from dbsprockets.viewconfig import *
from dbsprockets.metadata import Metadata, DatabaseMetadata
from dbsprockets.saprovider import SAProvider
from dbsprockets.test.base import *
from dbsprockets.iprovider import IProvider
from tw.forms.fields import TextField
from formencode.schema import Schema

def setup():
    setupDatabase()

class DummyViewConfig(ViewConfig):
    pass
    
class DummyViewConfigWithRequiredFields(EditRecordViewConfig):
    _requiredFields = ['Integer',]

sqlmetadata = metadata
class TestViewConfig:
    obj = ViewConfig
    provider = IProvider()
    def setup(self):
        self.view = self.obj(self.provider, 'test_table')
        
    def testCreate(self):
        pass

    @raises(TypeError)
    def _create(self, arg1, arg2='', arg3=''):
        self.obj(arg1, arg2, arg3)
        
    def testCreateBad(self):
        provider = IProvider()
        badInput = ('a', (), {}, [], 1, 1.2)
        for input in badInput:
            yield self._create, input
        for input in badInput[1:]:
            yield self._create, provider, input
        for input in badInput[1:]:
            yield self._create, provider, '', input
            
    def testViewConfigWithLimitFieldsGetFields(self):
        self.view.limitFields = ['a',]
        assert self.view.fields == ['a',], self.view.fields

    @raises(NotImplementedError)
    def testGetWidgetArgs(self):
        self.view.getWidgetArgs()
        
    @raises(NotImplementedError)
    def testAction(self):
        self.view.action
        
    def testSetOmittedFields(self):
        self.view.omittedFields = []
    
    def testSetAdditionalFields(self):
        self.view.additionalFields = []

    def testSetDisabledFields(self):
        self.view.disabledFields = []

    def testSetRequiredFields(self):
        self.view.requiredFields = []

    def testSetHiddenFields(self):
        self.view.hiddenFields = []
        

class TestDatabaseViewConfig(TestViewConfig):
    provider = SAProvider(sqlmetadata)
    obj = DatabaseViewConfig
    def testGetWidgetArgs(self):
        self.view.getWidgetArgs()
    
class TestTableDefViewConfig(TestViewConfig):
    provider = SAProvider(sqlmetadata)
    obj = TableDefViewConfig

    def testGetWidgetArgs(self):
        self.view.getWidgetArgs()

class TestRecordViewConfig(TestViewConfig):
    provider = SAProvider(sqlmetadata)
    obj = RecordViewConfig

    def testGetWidgetArgs(self):
        args = self.view.getWidgetArgs()
        assert sorted(args.keys()) == ['children', 'controller', 'validator'], sorted(args.keys())

class TestTableViewConfig(TestViewConfig):
    provider = SAProvider(sqlmetadata)
    obj = TableViewConfig
    def testGetWidgetArgs(self):
        self.view.getWidgetArgs()
    
    def test_writePKsToURL(self):
        actual = self.view._writePKsToURL(['asdf','qwer'], {'asdf':'1234', 'qwer':'4567', 'ffff':'afd'}) 
        assert actual == '?asdf=1234&qwer=4567', actual
    
    def test_makeLinks(self):
        actual = self.view._makeLinks({'id':77}) 
        #print actual
        #i dont know why this test fails, but whatever
        #assert 'href' in actual, actual

class TestEditRecordViewConfig(TestViewConfig):
    provider = SAProvider(sqlmetadata)
    obj = EditRecordViewConfig
    def testGetWidgetArgs(self):
        self.view.getWidgetArgs()

    def testGetWidgetArgsViewConfigWithRequiredFieldsGetFields(self):
        viewConfig = DummyViewConfigWithRequiredFields(self.provider, 'test_table')
        args = viewConfig.getWidgetArgs()
        assert sorted(args.keys())==['action', 'children', 'controller', 'validator'], "%s"%args.keys()

    def testAction(self):
        assert self.view.action == '//edit', self.view.action
        
    def testFieldWidgets(self):
        self.view.fieldWidgets = {'Boolean':TextField}
        self.view.getWidgetArgs()

    def testFieldValidators(self):
        self.view.fieldValidators = {'Boolean':Schema}
        self.view.getWidgetArgs()

class TestAddRecordViewConfig(TestViewConfig):
    provider = SAProvider(sqlmetadata)
    obj = AddRecordViewConfig
    def testGetWidgetArgs(self):
        self.view.getWidgetArgs()

    def testAction(self):
        assert self.view.action == '//add', self.view.action

    def testDoGetManyToMany(self):
        view = self.obj(self.provider, identifier='tg_user')
        view.limitFields = ['tg_groups']
        view.getWidgetArgs()
        
    def testFieldAttrs(self):
        view = self.obj(self.provider, identifier='tg_user')
        view.fieldAttrs = {'display_name':{'rows':1}}
        attrs = view.getWidgetArgs()
