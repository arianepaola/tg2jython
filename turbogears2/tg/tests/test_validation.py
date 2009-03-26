# -*- coding: utf-8 -*-

import tg, pylons
from tg.controllers import TGController
from tg.decorators import expose, validate
from routes import Mapper
from routes.middleware import RoutesMiddleware
from formencode import validators, Schema
from simplejson import loads

from tg.tests.base import TestWSGIController, make_app, setup_session_dir, teardown_session_dir

def setup():
    setup_session_dir()
def teardown():
    teardown_session_dir()

from tw.forms import TableForm, TextField, CalendarDatePicker, SingleSelectField, TextArea
from tw.api import WidgetsList

class MyForm(TableForm):
    # This WidgetsList is just a container
    class fields(WidgetsList):
        title=TextField(validator=validators.NotEmpty())
        year = TextField(size=4, validator=validators.Int())
        
#then, we create an instance of this form
myform = MyForm("my_form", action='create')

class Pwd(Schema):
    pwd1 = validators.String(not_empty=True)
    pwd2 = validators.String(not_empty=True)
    chained_validators = [validators.FieldsMatch('pwd1', 'pwd2')]

class BasicTGController(TGController):

    @expose('json')
    @validate(validators={"some_int": validators.Int()})
    def validated_int(self, some_int):
        assert isinstance(some_int, int)
        return dict(response=some_int)
    
    @expose('json')
    @validate(validators={"a":validators.Int()})
    def validated_and_unvalidated(self, a, b):
        assert isinstance(a, int)
        assert isinstance(b, unicode)
        return dict(int=a,str=b)

    @expose('json')
    @validate(validators={"a":validators.Int(), "b":validators.Email})
    def two_validators(self, a=None, b=None, *args):
        errors = pylons.c.form_errors
        values =  pylons.c.form_values
        return dict(a=a, b=b, errors=str(errors), values=str(values))

    @expose()
    def display_form(self, **kwargs):
        return str(myform.render(values=kwargs))

    @expose('json')
    @validate(form=myform)
    def process_form(self, **kwargs):
        kwargs['errors'] = pylons.c.form_errors
        return dict(kwargs)
    
    @expose('json')
    @validate(form=myform, error_handler=process_form)
    def send_to_error_handler(self, **kwargs):
        kwargs['errors'] = pylons.c.form_errors
        return dict(kwargs)

    @expose()    
    @validate(validators=Pwd())
    def password(self, pwd1, pwd2):
        if pylons.c.form_errors:
            return "There was an error"
        else:
            return "Password ok!"
        
class TestTGController(TestWSGIController):
    def __init__(self, *args, **kargs):
        TestWSGIController.__init__(self, *args, **kargs)
        self.app = make_app(BasicTGController)
        
    def test_basic_validation_and_jsonification(self):
        "Ensure you can pass in a dictionary of validators"
        form_values = {"some_int":22}
        resp = self.app.post('/validated_int', form_values)
        assert '{"response": 22}'in resp
        
    def test_for_other_params_after_validation(self):
        "Ensure that both validated and unvalidated data make it through"
        form_values = {'a':1, 'b':"string"}
        resp = self.app.post('/validated_and_unvalidated', form_values)
        assert '"int": 1' in resp
        assert '"str": "string"' in resp
    
    def test_two_validators_errors(self):
        "Ensure that multiple validators are applied correctly"
        form_values = {'a':'1', 'b':"guido@google.com"}
        resp = self.app.post('/two_validators', form_values)
        content = loads(resp.body)
        assert content['a'] == 1
                
    def test_validaton_errors(self):
        "Ensure that dict validation produces a full set of errors"
        form_values = {'a':'1', 'b':"guido~google.com"}
        resp = self.app.post('/two_validators', form_values)
        print resp
        assert 'An email address must contain a single @' in resp
    
    def test_form_validation(self):
        "Check @validate's handing of ToscaWidget forms instances"
        form_values = {'title':'Razer', 'year':"2007"}
        resp = self.app.post('/process_form', form_values)
        print resp
        values = loads(resp.body)
        assert values['year'] == 2007
    
    def test_form_render(self):
        'Test that myform renders properly'
        resp = self.app.post('/display_form')
        print resp
        assert 'id="my_form_title.label"' in resp
        assert 'class="fieldlabel required"' in resp
        assert "Title" in resp
    
    def test_form_validation_error(self):
        "Test validation form vaidation (with errors)"
        form_values = {'title':'Razer', 'year':"t007"}
        resp = self.app.post('/process_form', form_values)
        values = loads(resp.body)
        print values['errors']
        assert  "Please enter an integer value" in values['errors']['year']

    def test_form_validation_error(self):
        "Test validation form vaidation (with errors)"
        form_values = {'title':'Razer', 'year':"t007"}
        resp = self.app.post('/send_to_error_handler', form_values)
        values = loads(resp.body)
        print values['errors']
        assert  "Please enter an integer value" in values['errors']['year']

    def test_form_validation_error(self):
        "Test schema vaidation"
        form_values = {'pwd1':'me', 'pwd2':"you"}
        resp = self.app.post('/password', form_values)
        assert "There was an error" in resp
        form_values = {'pwd1':'you', 'pwd2':"you"}
        resp = self.app.post('/password', form_values)
        assert "Password ok!" in resp

