from util import WebHelpersTestCase
import unittest

from webhelpers.rails.form_options import *

class TestFormOptionsHelper(WebHelpersTestCase):
    def test_array_options_for_select(self):
        self.assertEqual(
            "<option value=\"&lt;Denmark&gt;\">&lt;Denmark&gt;</option>\n<option value=\"USA\">USA</option>\n<option value=\"Sweden\">Sweden</option>",
            options_for_select([ "<Denmark>", "USA", "Sweden" ]))

    def test_array_options_for_select_with_selection(self):
        self.assertEqual(
            "<option value=\"Denmark\">Denmark</option>\n<option value=\"&lt;USA&gt;\" selected=\"selected\">&lt;USA&gt;</option>\n<option value=\"Sweden\">Sweden</option>",
            options_for_select([ "Denmark", "<USA>", "Sweden" ], "<USA>"))

    def test_array_options_for_select_with_selection_array(self):
        self.assertEqual(
            "<option value=\"Denmark\">Denmark</option>\n<option value=\"&lt;USA&gt;\" selected=\"selected\">&lt;USA&gt;</option>\n<option value=\"Sweden\" selected=\"selected\">Sweden</option>",
            options_for_select([ "Denmark", "<USA>", "Sweden" ], [ "<USA>", "Sweden" ]))

    def test_array_options_for_string_include_in_other_string_bug_fix(self):
        self.assertEqual(
            "<option value=\"ruby\">ruby</option>\n<option value=\"rubyonrails\" selected=\"selected\">rubyonrails</option>",
            options_for_select([ "ruby", "rubyonrails" ], "rubyonrails"))
        self.assertEqual(
            "<option value=\"ruby\" selected=\"selected\">ruby</option>\n<option value=\"rubyonrails\">rubyonrails</option>",
            options_for_select([ "ruby", "rubyonrails" ], "ruby"))
        self.assertEqual(
            '<option value="ruby" selected="selected">ruby</option>\n<option value="rubyonrails">rubyonrails</option>\n<option value=""></option>',
            options_for_select([ "ruby", "rubyonrails", None ], "ruby"))

    def test_hash_options_for_select_with_dict(self):
        self.assertEqual(
            '<option value="Dollar">$</option>\n<option value="&lt;Kroner&gt;">&lt;DKR&gt;</option>',
            options_for_select({ "$": "Dollar", "<DKR>": "<Kroner>" }))
        self.assertEqual(
            '<option value="Dollar" selected="selected">$</option>\n<option value="&lt;Kroner&gt;">&lt;DKR&gt;</option>',
            options_for_select({ "$": "Dollar", "<DKR>": "<Kroner>" }, "Dollar"))
        self.assertEqual(
            '<option value="Dollar" selected="selected">$</option>\n<option value="&lt;Kroner&gt;" selected="selected">&lt;DKR&gt;</option>',
            options_for_select({ "$": "Dollar", "<DKR>": "<Kroner>" }, [ "Dollar", "<Kroner>" ]))

    def test_options_for_select_from_objects(self):
        class Something(object):
            select_name = "something"
            select_value = "The Something"
        class SomethingElse(object):
            select_name = "somethingelse"
            select_value = "The Something Else"
        self.assertEqual('<option value="something">something</option>\n<option value="somethingelse">somethingelse</option>',
                         options_for_select_from_objects([Something(), SomethingElse()], 'select_name'))
        self.assertEqual('<option value="something" selected="selected">something</option>\n<option value="somethingelse">somethingelse</option>',
                         options_for_select_from_objects([Something(), SomethingElse()], 'select_name', selected='something'))
        self.assertEqual('<option value="The Something">something</option>\n<option value="The Something Else">somethingelse</option>',
                         options_for_select_from_objects([Something(), SomethingElse()], 'select_name', 'select_value'))
        self.assertEqual('<option value="The Something" selected="selected">something</option>\n<option value="The Something Else">somethingelse</option>',
                         options_for_select_from_objects([Something(), SomethingElse()], 'select_name', 'select_value', 'The Something'))

    def test_options_for_select_from_dicts(self):
        something = dict(select_name="something",
                         select_value="The Something")
        somethingelse = dict(select_name="somethingelse",
                         select_value="The Something Else")
        self.assertEqual('<option value="something">something</option>\n<option value="somethingelse">somethingelse</option>',
                         options_for_select_from_dicts([something, somethingelse], 'select_name'))
        self.assertEqual('<option value="something" selected="selected">something</option>\n<option value="somethingelse">somethingelse</option>',
                         options_for_select_from_dicts([something, somethingelse], 'select_name', selected='something'))
        self.assertEqual('<option value="The Something">something</option>\n<option value="The Something Else">somethingelse</option>',
                         options_for_select_from_dicts([something, somethingelse], 'select_name', 'select_value'))
        self.assertEqual('<option value="The Something" selected="selected">something</option>\n<option value="The Something Else">somethingelse</option>',
                         options_for_select_from_dicts([something, somethingelse], 'select_name', 'select_value', 'The Something'))
    
if __name__ == '__main__':
    suite = [unittest.makeSuite(TestFormOptionsHelper)]
    for testsuite in suite:
        unittest.TextTestRunner(verbosity=1).run(testsuite)
