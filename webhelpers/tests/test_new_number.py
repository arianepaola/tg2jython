from nose.tools import eq_

from webhelpers.number import *

class TestFormatNumber(object):
    def test_positive(self):
        eq_(format_number(1234567.89), "1,234,567.89")
        eq_(format_number(1234567), "1,234,567")
        eq_(format_number(123456), "123,456")
        eq_(format_number(12345), "12,345")
        eq_(format_number(1234), "1,234")
        eq_(format_number(123), "123")
        eq_(format_number(12), "12")
        eq_(format_number(1), "1")
        eq_(format_number(123.4), "123.4")

    def test_negative(self):
        eq_(format_number(-1234567.89), "-1,234,567.89")
        eq_(format_number(-1234567), "-1,234,567")
        eq_(format_number(-123456), "-123,456")
        eq_(format_number(-12345), "-12,345")
        eq_(format_number(-1234), "-1,234")
        eq_(format_number(-123), "-123")
        eq_(format_number(-12), "-12")
        eq_(format_number(-1), "-1")
        
    def test_other(self):
        eq_(format_number(1234.5, " ", ","), "1 234,5")
        eq_(format_number(1234.5, ".", ","), "1.234,5")
        eq_(format_number(-1234.5, ".", ","), "-1.234,5")
