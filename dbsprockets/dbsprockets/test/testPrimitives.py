from dbsprockets.primitives import *
from dbsprockets.test.model import *
from dbsprockets.test.base import setupDatabase, session
from tw.forms.fields import PasswordField
from tw.forms import Form
from formencode.validators import FieldsMatch
from formencode import Schema
from nose.tools import raises, eq_
from difflib import ndiff


def setup():
    setupDatabase()
    import dbsprockets.primitives as p
    p.generator = SprocketGenerator()
    p.fetcher = DataFetcher()
    p.makeForm = p.generator.makeForm
    p.makeTable = p.generator.makeTable
    p.getTableValue = p.fetcher.getTableValue
    p.SAORMDBHelper = p._SAORMDBHelper()
    global makeForm, makeTable, getTableValue
    makeForm = p.makeForm
    makeTable = p.makeTable
    getTableValue = p.getTableValue

class TestDBHelper:
    
    def setup(self):
        self.helper = DBHelper()
        
    @raises(NotImplementedError)
    def testGetMetadata(self):
        self.helper.getMetadata(None)
        
    @raises(NotImplementedError)
    def testGetIdentifier(self):
        self.helper.getIdentifier(None)
    
    @raises(NotImplementedError)
    def testValidateModel(self):
        self.helper.validateModel(None)
    
class TestSAORMHelper:
    
    def setup(self):
        self.helper = SAORMDBHelper
        
    @raises(TypeError)
    def testValidateModelBad(self):
        self.helper.validateModel(None)

    @raises(Exception)
    def testValidateModelBadNoFields(self):
        class Dummy:
            c = {}
            
        self.helper.validateModel(Dummy)
        
class TestDatabaseMixin:
    
    def setup(self):
        self.mixin = DatabaseMixin()
        
    def testCreate(self):
        pass

    @raises(Exception)
    def test_getHelperBad(self):
        self.mixin._getHelper(None)
        
        
@raises(Exception)
def _create(model, 
             action, 
             identifier='',
             controller='',
             hiddenFields=[],
             disabledFields=[],
             requiredFields=[], 
             omittedFields=[], 
             additionalFields=[], 
             limitFields=None,
             fieldAttrs={},
             widgets={},
             validators={},
             formValidator=None,
             checkIfUnique=True):
    makeForm(model=model, 
             action=action, 
             identifier=identifier, 
             controller=controller,
             hiddenFields=hiddenFields,
             disabledFields=disabledFields,
             requiredFields=reduce,
             omittedFields=omittedFields,
             additionalFields=additionalFields,
             limitFields=limitFields,
             fieldAttrs=fieldAttrs,
             widgets=widgets,
             validators=validators,
             formValidator=formValidator, 
             checkIfUnique=checkIfUnique)

def testMakeFormBad():
    badInput = ('a', (), [], 1, 1.2, False, {}, None)
    for input in badInput[1:]:
        yield _create, User, input
    for input in badInput[1:]:
        yield _create, User, 'a', input
    for input in badInput[1:]:
        yield _create, User, 'a', 'a', input
    badInput = ('a', 1, 1.2, False, {}, None)
    for input in badInput:
        yield _create, User, 'a', 'a', 'a', input
    for input in badInput:
        yield _create, User, 'a', 'a', 'a', [], input
    for input in badInput:
        yield _create, User, 'a', 'a', 'a', [], [], input
    for input in badInput:
        yield _create, User, 'a', 'a', 'a', [], [], [], input
    badInput = ('a', 1, 1.2, False, (),)
    for input in badInput:
        yield _create, User, 'a', 'a', 'a', [], [], [], [], input

    badInput = ('a', 1, 1.2, False, None)
    for input in badInput:
        yield _create, User, 'a', 'a', 'a', [], [], [], [], [], input
        
    badInput = ('a', 1, 1.2, False, (), [], None)
    for input in badInput:
        yield _create, User, 'a', 'a', 'a', [], [], [], [], [], None, input
    badInput = ('a', 1, 1.2, False, (), [],)
    for input in badInput:
        yield _create, User, 'a', 'a', 'a', [], [], [], [], [], None, {}, input
    for input in badInput:
        yield _create, User, 'a', 'a', 'a', [], [], [], [], [], None, {}, {}, input
    for input in badInput:
        yield _create, User, 'a', 'a', 'a', [], [], [], [], [], None, {}, {}, {}, input
    badInput = ('a', 1, 1.2, (), [], {},)
    for input in badInput:
        yield _create, User, 'a', 'a', 'a', [], [], [], [], [], None, {}, {}, {}, None, input
    
def testMakeForm():
    form = makeForm(User, 'add')
    rendered = form()
    assert rendered.endswith("""</tr><tr class="even">
            <th>
            </th>
            <td>
                <input type="submit" class="submitbutton" id="EditableRecordViewConfig_tg_user_submit" value="Submit" />
            </td>
        </tr>
    </table>
</form>"""), rendered
    
def testMakeFormWithHiddenFields():
    form = makeForm(User, 'add', hiddenFields=['email_address', 'tg_groups', 'town', 'password', 'display_name'])
    rendered = form()
    assert """<input type="hidden" name="town" class="hiddenfield" id="EditableRecordViewConfig_tg_user_town" value="" />
            <input type="hidden" name="password" class="hiddenfield" id="EditableRecordViewConfig_tg_user_password" value="" />""" in rendered, rendered

def testMakeFormWithlimitFields():
    form = makeForm(User, 'add', limitFields=['user_name', 'password'])
    rendered = form()
    assert """<tr class="even">
            <th>
                <label id="EditableRecordViewConfig_tg_user_user_name.label" for="EditableRecordViewConfig_tg_user_user_name" class="fieldlabel">User Name</label>
            </th>
            <td>
                <input type="text" name="user_name" class="textfield" id="EditableRecordViewConfig_tg_user_user_name" value="" maxlength="16" size="16" />
            </td>
        </tr>""" in rendered, rendered

def testMakeFormWithOmittedFields():
    form = makeForm(User, 'add', omittedFields=['email_address', 'tg_groups', 'town', 'password', 'display_name'])
    rendered = form()
    assert 'password' not in rendered, rendered

def testMakeFormWithWidgetType():
    form = makeForm(User, 'add', omittedFields=['email_address', 'tg_groups', 'town', 'password', 'display_name'], formWidgetType=Form)
    rendered = form()
    assert """<form xmlns="http://www.w3.org/1999/xhtml" id="EditableRecordViewConfig_tg_user" action="add" method="post" class="required form">
    <div>""" in rendered, rendered

def testMakeFormWithAdditionalField():
    form = makeForm(User, 'add', omittedFields=['email_address', 'tg_groups', 'town', 'password', 'display_name'])
    rendered = form()
    assert 'password' not in rendered, rendered

def testMakeFormWithDisabledField():
    form = makeForm(User, 'add', disabledFields=['user_id',])
    rendered = form()
    assert """<th>
                <label id="EditableRecordViewConfig_tg_user_user_id.label" for="EditableRecordViewConfig_tg_user_user_id" class="fieldlabel">User Id</label>
            </th>
            <td>
                <input type="text" name="user_id" class="textfield" id="EditableRecordViewConfig_tg_user_user_id" value="" disabled="disabled" />
            </td>
        </tr>""" in rendered, rendered

def testMakeFormUltimateUseCase():
    requiredFields = ['user_name',]
    omittedFields  = ['enabled', 'user_id', 'tg_groups', 'created', 'town', 'password', 'email_address', 'display_name']
    additionalFields = [PasswordField('passwordVerification', label_text='Verify'),]
    formValidator =  Schema(chained_validators=(FieldsMatch('password',
                                                            'passwordVerification',
                                                            messages={'invalidNoMatch': 
                                                                      "Passwords do not match"}),))
    
    form = makeForm(User, 'add', 
                    requiredFields=requiredFields, 
                    omittedFields=omittedFields, 
                    additionalFields=additionalFields, 
                    formValidator=formValidator)
    
    rendered = form()
    assert rendered == """<form xmlns="http://www.w3.org/1999/xhtml" id="EditableRecordViewConfig_tg_user" action="add" method="post" class="dbsprocketstableform required">
    <div>
            <input type="hidden" name="tableName" class="hiddenfield" id="EditableRecordViewConfig_tg_user_tableName" value="" />
            <input type="hidden" name="dbsprockets_id" class="hiddenfield" id="EditableRecordViewConfig_tg_user_dbsprockets_id" value="" />
    </div>
    <table border="0" cellspacing="0" cellpadding="2">
        <tr class="even">
            <th>
                <label id="EditableRecordViewConfig_tg_user_user_name.label" for="EditableRecordViewConfig_tg_user_user_name" class="fieldlabel required">User Name</label>
            </th>
            <td>
                <input type="text" name="user_name" class="textfield required" id="EditableRecordViewConfig_tg_user_user_name" value="" maxlength="16" size="16" />
            </td>
        </tr><tr class="odd">
            <th>
                <label id="EditableRecordViewConfig_tg_user_passwordVerification.label" for="EditableRecordViewConfig_tg_user_passwordVerification" class="fieldlabel">Verify</label>
            </th>
            <td>
                <input type="password" name="passwordVerification" class="passwordfield" id="EditableRecordViewConfig_tg_user_passwordVerification" value="" />
            </td>
        </tr><tr class="even">
            <th>
            </th>
            <td>
                <input type="submit" class="submitbutton" id="EditableRecordViewConfig_tg_user_submit" value="Submit" />
            </td>
        </tr>
    </table>
</form>""", rendered

#this test is conflicting with the dbmechanic tests
def testMakeTableWithData():
    actual = getTableValue(User)
    table = makeTable(User, '/')
    rendered = table(value=actual)
    assert """<table xmlns="http://www.w3.org/1999/xhtml" id="TableViewConfig_tg_user" class="grid" cellpadding="0" cellspacing="1" border="0">
    <thead>
        <tr>
            <th class="col_0">
            </th><th class="col_1">
            user_id
            </th><th class="col_2">
            user_name
            </th><th class="col_3">
            email_address
            </th><th class="col_4">
            display_name
            </th><th class="col_5">
            password
            </th><th class="col_6">
            town
            </th><th class="col_7">
            created
            </th><th class="col_8">
            tg_groups
            </th>
        </tr>
    </thead>
    <tbody>
        <tr class="even">
            <td><a href="//editRecord/tg_user?user_id=1">edit</a>|<a href="//delete/tg_user?user_id=1">delete</a></td><td>1</td><td>asdf</td><td></td><td></td><td>******</td><td>Arvada</td><td>""" in rendered, rendered

def testMakeTableWithDataAndNoController():
    actual = getTableValue(User)
    table = makeTable(User)
    rendered = table(value=actual)
    assert """<table xmlns="http://www.w3.org/1999/xhtml" id="TableViewConfig_tg_user" class="grid" cellpadding="0" cellspacing="1" border="0">
    <thead>
        <tr>
            <th class="col_0">
            user_id
            </th><th class="col_1">
            user_name
            </th><th class="col_2">
            email_address
            </th><th class="col_3">
            display_name
            </th><th class="col_4">
            password
            </th><th class="col_5">
            town
            </th><th class="col_6">
            created
            </th><th class="col_7">
            tg_groups
            </th>
        </tr>
    </thead>
    <tbody>
        <tr class="even">
            <td>1</td><td>asdf</td><td></td><td></td><td>******</td><td>Arvada</td>""" in rendered, rendered

#this test is conflicting with the dbmechanic tests
def testGetTableValue():
    actual = getTableValue(User)
    expected = [{u'town': u'Arvada', u'user_id': 1,
      u'email_address': None, u'display_name': None, u'password': '******', u'user_name': u'asdf'}]
    for i, item in enumerate(expected):
        for key, value in item.iteritems():
            assert actual[i][key] == value

#this test is conflicting with the dbmechanic tests
def testMakeRecordValue():
    actual = makeRecordView(User)
    value = {u'town': u'Arvada', u'user_id': 1,
      u'email_address': None, u'display_name': None, u'password': '******', u'user_name': u'asdf', 'created':None}
#    print actual.render(value)
    actual = actual.render(value)
    expected = """<table xmlns="http://www.w3.org/1999/xhtml" id="RecordViewConfig_tg_user" class="recordviewwidget">
<tr><th>Name</th><th>Value</th></tr>
<tr class="recordfieldwidget">
    <td>
        <b>user_id</b>
    </td>
    <td> 1
    </td>
</tr>
<tr class="recordfieldwidget">
    <td>
        <b>user_name</b>
    </td>
    <td> asdf
    </td>
</tr>
<tr class="recordfieldwidget">
    <td>
        <b>email_address</b>
    </td>
    <td>
    </td>
</tr>
<tr class="recordfieldwidget">
    <td>
        <b>display_name</b>
    </td>
    <td>
    </td>
</tr>
<tr class="recordfieldwidget">
    <td>
        <b>password</b>
    </td>
    <td> ******
    </td>
</tr>
<tr class="recordfieldwidget">
    <td>
        <b>town</b>
    </td>
    <td> Arvada
    </td>
</tr>
<tr class="recordfieldwidget">
    <td>
        <b>created</b>
    </td>
    <td>
    </td>
</tr>
<input type="hidden" name="dbsprockets_id" class="hiddenfield" id="RecordViewConfig_tg_user_dbsprockets_id" value="townuser_idcreateduser_namedisplay_namepasswordemail_address" />
</table>"""
    assert actual == expected, ''.join(a for a in ndiff(expected.splitlines(1), actual.splitlines(1)))
    
class TestSAORMDBHelperSAORMDBHelper:
    def setup(self):
        self.helper = SAORMDBHelper
    
    def testGetIdentifier(self):
        eq_(self.helper.getIdentifier(User), 'tg_user')
        
def testGetFormDefaults():
    actual = getFormDefaults(Example)
    assert sorted(actual.keys()) == ['Integer', 'created'], sorted(actual.keys())
    assert actual['Integer'] == 10

