from util import WebHelpersTestCase
import unittest

from webhelpers.rails.tags import *

class TestTagHelper(WebHelpersTestCase):
    def test_tag(self):
        self.assertEqual("<p class=\"show\" />", tag("p", class_='show'))
        self.assertEqual("<br>", tag("br", True))
    
    def test_tag_options(self):
        self.assertEqual("<p class=\"elsewhere\" />", tag("p", class_='elsewhere'))
    
    def test_tag_options_reject_none_option(self):
        self.assertEqual("<p />", tag("p", ignored=None))
    
    def test_tag_options_accept_blank_option(self):
        self.assertEqual("<p included=\"\" />", tag("p", included=''))
    
    def test_tag_options_converts_boolean_option(self):
        self.assertEqual('<p disabled="disabled" multiple="multiple" readonly="readonly" />',
               tag("p", disabled=True, multiple=True, readonly=True))
        self.assertEqual('<input disabled="disabled" type="text" />',
                         tag("input", type='text', disabled=True))
        
    def test_tag_options_double_escaped(self):
        self.assertEqual('<p included="AT&amp;amp;T" />', tag("p", included='AT&amp;amp;T'))
    
    def test_content_tag(self):
        self.assertEqual("<a href=\"create\">Create</a>", content_tag("a", "Create", href="create"))

    def test_escape_once(self):
        self.assertEqual("1 &lt; 2 &amp; 3", escape_once("1 < 2 &amp; 3"))

    def test_cdata_section(self):
        self.assertEqual('<![CDATA[Hello]]>', cdata_section('Hello'))
        self.assertEqual('<![CDATA[]]>', cdata_section(None))
    
        
if __name__ == '__main__':
    suite = [unittest.makeSuite(TestTagHelper)]
    for testsuite in suite:
        unittest.TextTestRunner(verbosity=1).run(testsuite)
