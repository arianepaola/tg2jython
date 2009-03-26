from tw.core.testutil import WidgetMixin
from tw.forms import DataGrid
from unittest import TestCase

class User(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age

class TestDatagrid(WidgetMixin, TestCase):
    TestWidget = DataGrid
    widget_kw = {
        'fields' : [('Name', 'name'), ('Age', 'age')],
        }

    def test_data_is_displayed(self):
        data = [User("User%d" % i, i) for i in xrange(10)]
        self.assertInOutput(
            ["User%d"%i for i in xrange(10)] + map(str, xrange(10)), data
            )
