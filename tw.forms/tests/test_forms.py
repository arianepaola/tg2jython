# -*- coding: utf-8 -*-
from unittest import TestCase
from tw.api import WidgetsList
from tw.forms import *
from tw.core.testutil import WidgetTestCase

from tw.forms.validators import (Int, String, UnicodeString, Schema, NotEmpty)
from formencode import Invalid
import formencode.api

from datetime import date, datetime

formencode.api.set_stdtranslation(languages=['C'])

#TODO: Use RequireMixin from tw.testutil to make sure tests that 
#      require an uninstalled template engine are skipped.

class TestSimpleInputWidget(WidgetTestCase):
    class TestWidget(InputWidget):
        params = ["show_error"]
        show_error = True
        template = """<div
            xmlns="http://www.w3.org/1999/xhtml"
            xmlns:py="http://genshi.edgewall.org/">
            <input type="text" value="${value}" name="${name}" id="${id}" />
            <span py:if="show_error and error" py:content="error" />
        </div>"""
        engine_name = "genshi"
        validator = Int
        default = 99
    

    def test_default_is_respected(self):
        self.assertInOutput('value="99"')

    def test_can_adjust_value(self):
        self.assertInOutput('value="2"', 2)

    def XXXtest_bad_value_raises_Invalid_when_rendering(self):
        #XXX: adjust_value is no longer called before rendering, adapt_value
        #     should be used instead
        self.assertRaises(Invalid, self.widget.render, "foo")

    def test_can_validate(self):
        self.failUnlessEqual(self.widget.validate("2"), 2)

    def test_can_coerce_py_value(self):
        self.failUnlessEqual(self.widget.validate(2), 2)

    def test_bad_value_raises_Invalid(self):
        self.assertRaises(Invalid, self.widget.validate, "foo")

    def test_explicit_error_is_displayed(self):
        try: self.widget.validate("foo")
        except Invalid, error: pass
        self.assertInOutput('Please enter an integer value', "foo", error=error)

    def test_error_is_displayed_from_request(self):
        try: self.widget.validate("foo")
        except Invalid: pass
        self.assertInOutput('Please enter an integer value', "foo")

    def test_no_error_is_displayed_if_explicity_told_to(self):
        try: self.widget.validate("foo")
        except Invalid, error: pass
        self.assertNotInOutput('Please enter an integer value', 
            "foo", error=error, show_error=False)

    def test_previous_input_is_displayed_from_request(self):
        value = self.value_at_request = 'foo'
        try: self.widget.validate(value)
        except Invalid: pass
        self.assertInOutput('foo')


class TestCanOverrideName(WidgetTestCase):
    """Tests that the id-derived name can be overriden with the ``name``
    keyword arg"""
    class TestWidget(InputWidget):
        template = '<div id="$id" name="$name" />'
    widget_kw = dict(name="somename")
    
    def test_can_override(self):
        self.assertInOutput(['id="test"', 'name="somename"'])
    





class TestNestedInputWidget(WidgetTestCase):
    class TestWidget(Form):
        class TextField(InputWidget):
            params = ["show_error"]
            show_error = True
            template = """<div
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:py="http://genshi.edgewall.org/">
                <input type="text" value="${value}" name="${name}" id="${id}" />
                <span py:if="show_error and error" py:content="error" />
            </div>"""
            engine_name = "genshi"
        children = [
            TextField("name", validator=String(not_empty=True)),
            TextField("friend", default="Japanese Friend's Name",
                      validator=UnicodeString()),
            TextField("age", validator=Int()),
            ]
        template = """<form
            xmlns="http://www.w3.org/1999/xhtml"
            xmlns:py="http://genshi.edgewall.org/">
            <ul>
                <li py:for="c in children" 
                    py:content="c.display(value_for(c), **args_for(c))" />
            </ul>
        </form>"""
        engine_name = "genshi"

    class Person(object):
        def __init__(self, name, age, friend=None):
            self.name = name; self.age = age; self.friend = friend
    


    def test_can_adjust_value(self):
        value = self.Person('alberto', 25)
        self.assertInOutput(['value="alberto"', 'value="25"'], value)

    def test_can_render_unicode(self):
        value = self.Person('alberto', 25, u'\u5bae\u672c')
        self.widget.render(value)

    def test_can_validate_unicode(self):
        value = {'name': 'alberto', 'friend': u'\u5bae\u672c',
                 'age': 25}
        expected = {'name': 'alberto', 'friend': u'\u5bae\u672c',
                    'age': 25}
        valid = self.widget.validate(value)
        self.failUnlessEqual(valid, expected)

    def test_can_redisplay_unicode(self):
        value = {'name': 'alberto', 'friend': u'\u5bae\u672c',
                 'age': "foo"}
        expected = {'name': 'alberto', 'friend': u'\u5bae\u672c',
                    'age': 25}
        try: self.widget.validate(value)
        except Invalid: pass
        self.widget.render()

    def test_can_render_validated_unicode(self):
        valid = self.widget.validate({'name': 'alberto',
                                      'friend': u'\u5bae\u672c', 'age': 25})
        self.widget.render(valid)

    def XXXtest_bad_value_raises_Invalid_when_rendering(self):
        #XXX: adjust_value is no longer called before rendering, adapt_value
        #     should be used instead
        value = self.Person('alberto', 'foo')
        self.assertRaises(Invalid, self.widget.render, value)

    def test_can_validate(self):
        value = {'name':'alberto', 'age':25, 'friend': u''}
        expected = {'name':'alberto', 'age':25, 'friend': u''}
        self.failUnlessEqual(self.widget.validate(value), expected)

    def test_can_coerce_good_value(self):
        value = {'name':'alberto', 'age':'25', 'friend': None}
        expected = {'name':'alberto', 'age':25, 'friend': u''}
        self.failUnlessEqual(self.widget.validate(value), expected)

    def test_bad_value_raises_Invalid(self):
        value = {'name':'alberto', 'age':'foo'}
        self.assertRaises(Invalid, self.widget.validate, value)

    def test_explicit_error_is_displayed(self):
        value = {'name':'alberto', 'age':'foo'}
        try: self.widget.validate(value)
        except Invalid, error: pass
        self.assertInOutput('Please enter an integer value', value, error=error)

    def test_error_is_displayed_from_request(self):
        value = {'name':'alberto', 'age':'foo'}
        try: self.widget.validate(value)
        except Invalid: pass
        self.assertInOutput('Please enter an integer value', value)

    def test_no_error_is_displayed_if_explicity_told_to(self):
        value = {'name':'alberto', 'age':'foo'}
        try: self.widget.validate(value)
        except Invalid, error: pass
        self.assertNotInOutput('Please enter an integer value', 
            value, error=error, 
            child_args=dict(age=dict(show_error=False))
            )

    def test_previous_input_is_displayed_from_request(self):
        self.value_at_request = value = {
            'name':'alberto', 'age':'foo'
            }
        try: self.widget.validate(value)
        except Invalid: pass
        self.assertInOutput(['alberto','foo'])

    def test_widget_places_error_and_values_in_request(self):
        value = {
            'name':'alberto', 'age':'foo'
            }
        try: self.widget.validate(value)
        except Invalid: pass
        self.assertInOutput(['alberto','foo', 'Please enter an integer value'])
        
    def test_inner_names_and_ids_are_generated_correctly(self):
        self.assertInOutput(
            ['name="%s"' % n for n in "name friend age".split()] + 
            ['id="test_%s"' % i for i in "name friend age".split()] 
            )

class TestRepeatingInputWidget(WidgetTestCase):
    class TestWidget(InputWidgetRepeater):
        class TextField(InputWidget):
            params = ["show_error"]
            show_error = True
            engine_name = "genshi"
            template = """<div
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:py="http://genshi.edgewall.org/">
                <input type="text" value="${value}" name="${name}" id="${id}" />
                <span py:if="show_error and error" py:content="error" />
            </div>"""
            validator = Int
        widget = TextField()


    def test_inner_names_and_ids_are_generated_correctly(self):
        self.assertInOutput(
            ['name="test-%d"' % n for n in range(3)])
        self.assertInOutput(
            ['id="test-%d"' % n for n in range(3)])

    def test_can_adjust_value(self):
        values = range(3)
        self.assertInOutput(
            ['value="%d"'%i for i in values], values)

    def XXXtest_bad_value_raises_Invalid_when_rendering(self):
        #XXX: adjust_value is no longer called before rendering, adapt_value
        #     should be used instead
        values = [0,1,"foo"]
        self.assertRaises(Invalid, self.widget.render, values)

    def test_can_validate(self):
        values = range(3)
        self.failUnlessEqual(
            self.widget.validate(values), map(Int.to_python, values)
            )

    def test_can_coerce_good_value(self):
        values = ["0","1","2"]
        self.failUnlessEqual(
            self.widget.validate(values), map(Int.to_python, values)
            )

    def test_bad_value_raises_Invalid(self):
        values = ["0","bar","2"]
        self.assertRaises(Invalid, self.widget.validate, values)

    def test_explicit_error_is_displayed(self):
        values = ["0","bar","2"]
        try: self.widget.validate(values)
        except Invalid, error: pass
        self.assertInOutput(
            'Please enter an integer value', values, error=error
            )

    def test_error_is_displayed_from_request(self):
        values = ["0","bar","2"]
        try: self.widget.validate(values)
        except Invalid: pass
        self.assertInOutput('Please enter an integer value', values)

    def test_no_error_is_displayed_if_explicity_told_to(self):
        values = ["0","bar","2"]
        child_args = [{}, {'show_error':False}, {}]
        try: self.widget.validate(values)
        except Invalid, error: pass
        self.assertNotInOutput('Please enter an integer value', 
            values, error=error, child_args=child_args)

    def test_error_is_assigned_to_correct_repetition(self):
        values = ["0","bar","2"]
        child_args = [{'show_error':False}, {}, {}]
        try: self.widget.validate(values)
        except Invalid, error: pass
        self.assertInOutput('Please enter an integer value', 
            values, error=error, child_args=child_args)

        values = ["0","bar","2"]
        child_args = [{}, {'show_error':False}, {}]
        try: self.widget.validate(values)
        except Invalid, error: pass
        self.assertNotInOutput('Please enter an integer value', 
            values, error=error, child_args=child_args)

    def test_previous_input_is_displayed_from_request(self):
        values = ["0","bar","2"]
        try: self.widget.validate(values)
        except Invalid: pass
        self.assertInOutput(values)


class TestFileUpload(WidgetTestCase):
    class TestWidget(Form):
        class Fields(WidgetsList):
            description = TextField()
            file = FileField()
        children = Fields()

    def test_enctype_is_set(self):
        self.assertInOutput('enctype')

class TestNestedFileUpload(WidgetTestCase):
    class TestWidget(Form):
        class Fields(WidgetsList):
            description = TextField()
            file = FileField()
        children = [FieldSet('fs', children=Fields())]

    def test_enctype_is_set(self):
        self.assertInOutput('enctype')

class TestNestedForms(WidgetTestCase):
    class TestWidget(Form):
        class Fields(WidgetsList):
            name = TextField()
            age = TextField()
        class InnerForm(Form):
            class InnerFields(WidgetsList):
                description = TextField()
                file = FileField()
            children = InnerFields()
        children = [InnerForm('inner')] + Fields()

    def test_enctype_is_set(self):
        self.assertInOutput('enctype')

    def test_correct_ids(self):
        self.assertInOutput(
            "test_inner_description test_inner_file test_name test_age".split()
            )
    def test_correct_names(self):
        self.assertInOutput(['name="%s"' % n for n in
            "inner.description inner.file name age".split()]
            )

class TestSimpleSingleSelectField(WidgetTestCase):
    TestWidget = SingleSelectField

    def test_simple_render(self):
        self.assertInOutput(
            ["select", "option", 'value="foo"'], options=["foo"]
            )

    def test_selected_appears(self):
        self.assertInOutput(
            ["select", "option", 'value="foo"', 'selected'], 
            "foo", options=["foo"]
            )

    def test_grouped_options(self):
        options = [
            ("Apples", ["apple1","apple2"]),
            ("Oranges", ["orange1","orange2"]),
            ]
        self.assertInOutput(
            ["optgroup", "Apples", "Oranges", "orange1", "apple2"], 
            options=options)
        self.assertInOutput("selected", "orange1", options=options)
        self.assertNotInOutput("selected", "orange3", options=options)


class TestSingleSelectFieldWithDefaultOption(WidgetTestCase):
    TestWidget = SingleSelectField
    widget_kw = {'default':"foo"}

    def test_simple_render(self):
        self.assertInOutput( ["selected"], options=["foo"])

class TestValidatingSingleSelectField(WidgetTestCase):
    TestWidget = SingleSelectField
    widget_kw = {'validator': Int}

    def test_simple_render(self):
        options = range(3)
        self.assertInOutput(
            ['value="%d"'%i for i in options] +
            ['>%s<'%i for i in options],
            options=options)

    def test_selected_appears(self):
        self.assertInOutput(
            ['selected'], 2, options=range(3)
            )
    
    def test_selected_appears_on_redisplay(self):
        self.assertInOutput(
            ['selected'], "2", options=range(3)
            )

    def test_selected_does_not_appear(self):
        self.assertNotInOutput(
            ['selected'], 4, options=range(3)
            )

    def test_selected_does_not_appear_on_redisplay(self):
        self.assertNotInOutput(
            ['selected'], "4", options=range(3)
            )

    def test_render_passing_tuple(self):
        options = list(enumerate("foo bar zoo".split()))
        self.assertInOutput(
            ['value="%d"'%i[0] for i in options] +
            ['>%s<'%i[1] for i in options], 
            options=options)

    def test_selected_passing_tuple(self):
        options = list(enumerate("foo bar zoo".split()))
        self.assertInOutput(['selected'], 2, options=options)
        self.assertNotInOutput(['selected'], 4, options=options)

class TestSingleSelectFieldEmptyValueNotEmptyValidator(WidgetTestCase):
    TestWidget = SingleSelectField
    widget_kw = {'validator': Int(not_empty=True)}

    def test_can_display(self):
        options = [None] + range(2)
        self.assertInOutput('value="" selected="selected"', options=options)

class TestFormFieldAlias(TestCase):

    def test_fields_are_attached_when_param(self):
        f = Form(fields=[TextField('foo')])
        self.failUnless(hasattr(f.c, 'foo'))
        
    def test_fields_are_attached_when_in_class(self):
        class MyForm(Form):
            fields = [TextField('foo')]
        f = MyForm()
        self.failUnless(hasattr(f.c, 'foo'))

class TestUnicode(WidgetTestCase):
    class TestWidget(TableForm):
        class fields(WidgetsList):
            name = TextField(validator=UnicodeString)
            age = TextField(validator=Int)
    def test_unicode_value_redisplays_if_validation_fails(self):
        value = {'name': u'\u5bae\u672c'.encode('utf-8'), 'age': 'foo'}
        try: self.widget.validate(value)
        except Invalid: pass
        self.assertInOutput(u'\u5bae\u672c')

    def test_None_not_in_output(self):
        self.assertNotInOutput('None')

class TestFormValidation(WidgetTestCase):
    class TestWidget(Form):
        fields = [
            FieldSet('fs', fields=[
                TextField('foo', validator=Int(not_empty=True)),
                ]),
            ]
    def test_variables_are_decoded(self):
        value = {'fs.foo':1}
        try: 
            self.widget.validate(value)
        except Invalid:
            self.fail()

class TestCheckBox(WidgetTestCase):
    TestWidget = CheckBox

    def test_is_checked(self):
        self.assertInOutput('checked', True)
        self.assertNotInOutput('checked', False)

    def test_validation(self):
        self.failUnlessEqual(self.widget.validate('on'), True)
        self.failUnlessEqual(self.widget.validate(None), False)


class TestSecureFormMixin(WidgetTestCase):

    class TestWidget(ListForm, SecureFormMixin):
        def session_secret_cb(self):
            return "my-secret-string", "user_name"

    bad_data = {'form_token__': '191880f1b701a0385b1569c4ca1f96cf'}
    good_data = {'form_token__': '4f431a86dd13907f11fbec3d6c0b03d9'}

    def test_output(self):
        self.assertInOutput(['<input type="hidden"',
                             'value="%s"' % self.good_data['form_token__']])
    
    def test_validation(self):
        self.assertRaises(Invalid, self.widget.validate, self.bad_data)
        self.assertEqual(self.widget.validate(self.good_data),
                         {'form_token__': None})

    def test_error_is_displayed_from_request(self):
        try: self.widget.validate(self.bad_data)
        except Invalid: pass
        self.assertInOutput("Form token mismatch")

class TestBooleanRadioButtonList(WidgetTestCase):
    TestWidget = BooleanRadioButtonList

    def test_render_python_value(self):
        self.assertInOutput('value="false" checked="checked"', False)
        self.assertInOutput('value="false" checked="checked"', 0)
        self.assertInOutput('value="true" checked="checked"', True)
        self.assertInOutput('value="true" checked="checked"', 1)

    def test_render_redisplayed_value(self):
        self.assertInOutput('value="false" checked="checked"', "false")
        self.assertInOutput('value="true" checked="checked"', "true")

class TestMixedSchemaAndWidgetValidation(WidgetTestCase):
    """Tests that we can place validators both in the widgets and in the
    form's Schema and the resulting Schema will have all."""
    class TestWidget(Form):
        validator = Schema(int2=Int, fs=Schema(int2=Int))
        class fields(WidgetsList):
            int1 = TextField(validator=Int)
            int2 = TextField()
            fs = FieldSet(
                children=[
                    TextField("int1", validator=Int),
                    TextField("int2"),
                    ])
    
    def test_validate_good(self):
        value = dict(int1="1", int2="2", fs=dict(int1="1", int2="2"))
        expected = dict(int1=1, int2=2, fs=dict(int1=1, int2=2))
        self.failUnlessEqual(self.widget.validate(value), expected)

    def test_validate_bad_from_outer_widget(self):
        value = dict(int1="bad", int2="2", fs=dict(int1="1", int2="2"))
        try: self.widget.validate(value)
        except Invalid, error: pass
        self.failUnless(error.error_dict.has_key('int1'))

    def test_validate_bad_from_outer_schema(self):
        value = dict(int1="1", int2="bad", fs=dict(int1="1", int2="2"))
        try: self.widget.validate(value)
        except Invalid, error: pass
        self.failUnless(error.error_dict.has_key('int2'))

    def test_validate_bad_from_inner_widget(self):
        value = dict(int1="1", int2="2", fs=dict(int1="bad", int2="2"))
        try: self.widget.validate(value)
        except Invalid, error: pass
        self.failUnless(error.error_dict['fs'].error_dict.has_key('int1'))

    def test_validate_bad_from_inner_schema(self):
        value = dict(int1="1", int2="2", fs=dict(int1="1", int2="bad"))
        try: self.widget.validate(value)
        except Invalid, error: pass
        self.failUnless(error.error_dict['fs'].error_dict.has_key('int2'))


class TestCalendarDatePicker(WidgetTestCase):
    widget = CalendarDatePicker('date')
    
    def test_works_with_date(self):
        self.assertInOutput(['value="01/01/1981"'], value=date(1981, 1, 1))
    
    def test_works_with_datetime(self):
        self.assertInOutput(['value="01/01/1981"'],
                            value=datetime(1981, 1, 1, 0, 0))

from formencode import ForEach

class AtLeastOne(ForEach):
    validator = Int
    def _to_python(self, value, state=None):
        value = super(AtLeastOne, self)._to_python(value, state)
        if len(value) < 1 or value is None:
            raise Invalid("at least one item must be selected", value, state)
        return value
    def empty_value(self, value):
        return self._to_python(value)

class ForEachMixinTest:
    def test_good_values(self):
        values = map(str, range(3))
        self.failUnlessEqual(self.widget.validate(values), range(3))

    def test_none_selected(self):
        values = []
        self.assertRaises(Invalid, self.widget.validate, values)

class TestForEachInstance(WidgetTestCase, ForEachMixinTest):
    widget = CheckBoxList(validator=AtLeastOne())

class TestForEachClass(WidgetTestCase, ForEachMixinTest):
    widget = CheckBoxList(validator=AtLeastOne)

class TestMultipleSelectionMixin(WidgetTestCase):
    class TestWidget(MultipleSelectionMixin, SelectionField):
        template = "$value"
        engine_name = "toscawidgets"

    def test_value_is_scalar(self):
        """Assert values that reach the template of a MultipleSelectionMixin are
        scalars (not lists as yielded by its ForEach validator."""
        self.failUnlessEqual(self.widget.display('foo'), 'foo')

    def test_no_value(self):
        self.failUnlessEqual(self.widget.display(), '')
            
    
class TestMultipleSelectField(WidgetTestCase):
    class TestWidget(ListForm):
        class fields(WidgetsList):
            id = TextField(validator=UnicodeString(not_empty=True))
            domain = MultipleSelectField(
                validator=Int,
                options = list(enumerate("abdc"))
                )
     
    def test_value_redisplays(self):
        value = dict(id="", domain=map(str, [1,2]))
        try: self.widget.validate(value)
        except Invalid, error: pass
        self.assertInOutput([
            'value="1" selected="selected"',
            'value="2" selected="selected"',
            ])

class TestStripName(WidgetTestCase):
    class TestWidget(ListForm):
        class fields(WidgetsList):
            fs = TableFieldSet(strip_name=True, fields=[
                TextField("a", validator=NotEmpty),
                TextField("b"),
                ])
    
    def test_ids_are_generated_properly(self):
        self.assertInOutput(["test_fs_a", "test_fs_b"])

    def test_names_are_generated_properly(self):
        self.assertInOutput(['name="a"', 'name="b"'])

    def test_values_are_passed_properly(self):
        self.assertInOutput(["foo", "bar"], dict(a="foo", b="bar"))

    def test_good_values_are_validated_properly(self):
        value = dict(a="foo", b="bar")
        self.failUnlessEqual(self.widget.validate(value), value)

    def test_bad_values_are_validated_properly(self):
        value = dict(a="foo")
        try:
            self.widget.validate(value)
        except Invalid, e:
            self.failUnless(e.error_dict and "b" in e.error_dict)
            # test error message is displayed properly
            self.assertInOutput("Missing value", error=e)
        else:
            self.fail("And exception should have been raised")
