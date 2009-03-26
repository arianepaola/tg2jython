from tw.core.testutil      import WidgetTestCase
from tw.api           import WidgetsList
from tw.forms import *
from formencode                 import Invalid, FancyValidator
from formencode.validators      import *
from formencode.schema          import Schema
from datetime                   import *
from datetime                   import datetime, timedelta

now = datetime.now()
tomorrow = now + timedelta(1)

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

class DateValidator(Schema):
    filter_extra_fields = True
    allow_extra_fields = True
    messages = {
        'invalidDate' : 'Please enter a valid date',
        'beforeTomorrow' : 'Please enter a date after tomorrow'
    }
    def _to_python(self, value, state=None):
        try:
            date = datetime(int(value['year']),
                            MONTHS.index(value['month'])+1,
                            int(value['day']))
        except:
            raise Invalid(self.message('invalidDate', state), state, value)
        if date < tomorrow:
            raise Invalid(self.message('beforeTomorrow', state), state, value)
        return date
    def _from_python(self, value, state=None):
        if not value:
            return None
        elif isinstance(value, datetime):
            return {'year' : str(value.year),
                    'month' : MONTHS[value.month-1],
                    'day' : str(value.day)}
        else:
            return value

class DateDropdown(ListFieldSet):
    force_conversion = True
    def adapt_value(self, value):
        # Need to bypass the default behaviour of adapt_value when a widget
        # has children because it will fetch the attributes form value which
        # match the children's id and put them into a dict
        # (eg: {'month': 6, 'day': 10, 'year': 2007})
        # An alternative would be to code the validator's from_python to take
        # this into account
        # TODO: Doucment this clearly
        return value

    class fields(WidgetsList):
        year = SingleSelectField(
            validator=Int,
            options=range(now.year, now.year+4),
            )
        day = SingleSelectField(
            validator=Int,
            options=range(1,32),
            )
        month = SingleSelectField(
            validator=String,
            options=MONTHS,
            )
    validator = DateValidator
    engine_name = 'genshi'
    template = '''<div>${display_child(c.year)} ${display_child(c.month)}
                  ${display_child(c.day)}</div>'''

class TestFromPythonInSchema(WidgetTestCase):
    """Tests that form's schema's from_python adjusts value"""  
    widget = DateDropdown(default = datetime(2007, 11, 17))
    
    def testMonthWithDefault(self):
        self.assertInOutput(
            '<option value="Nov" selected="selected">Nov</option>')

    def testMonthWithInput(self):
        self.assertInOutput(
            '<option value="Jun" selected="selected">Jun</option>',
            datetime(2007, 06, 10))



# Alternative version using adapt_value instead of from_python (preferred)
class DateValidatorAlt(Schema):
    filter_extra_fields = True
    allow_extra_fields = True
    messages = {
        'invalidDate' : 'Please enter a valid date',
        'beforeTomorrow' : 'Please enter a date after tomorrow'
    }
    def _to_python(self, value, state=None):
        try:
            date = datetime(int(value['year']),
                            MONTHS.index(value['month'])+1,
                            int(value['day']))
        except:
            raise Invalid(self.message('invalidDate', state), state, value)
        if date < tomorrow:
            raise Invalid(self.message('beforeTomorrow', state), state, value)
        return date

class DateDropdownAlt(ListFieldSet):
    def adapt_value(self, value):
        if isinstance(value, datetime):
            return {'year' : str(value.year),
                    'month' : MONTHS[value.month-1],
                    'day' : str(value.day)}
        return super(ListFieldSet, self).adapt_value(value)

    class fields(WidgetsList):
        year = SingleSelectField(
            validator=Int,
            options=range(now.year, now.year+4),
            )
        day = SingleSelectField(
            validator=Int,
            options=range(1,32),
            )
        month = SingleSelectField(
            validator=String,
            options=MONTHS,
            )
    validator = DateValidatorAlt
    engine_name = 'genshi'
    template = '''<div>${display_child(c.year)} ${display_child(c.month)}
                  ${display_child(c.day)}</div>'''

class TestFromPythonInSchemaAlt(WidgetTestCase):
    """Tests that form's schema's from_python adjusts value"""  
    widget = DateDropdown(default = datetime(2007, 11, 17))
    
    def testMonthWithDefault(self):
        self.assertInOutput(
            '<option value="Nov" selected="selected">Nov</option>')

    def testMonthWithInput(self):
        self.assertInOutput(
            '<option value="Jun" selected="selected">Jun</option>',
            datetime(2007, 06, 10))
