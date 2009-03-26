# -*- coding: utf-8 -*-
from util import WebHelpersTestCase
import unittest

from webhelpers.html import HTML
from webhelpers.html.tags import *

class TestFormTagHelper(WebHelpersTestCase):
    def test_check_box(self):
        self.assertEqual(
            checkbox("admin"),
            u'<input name="admin" type="checkbox" value="1" />',
        )

    def test_form(self):
        self.assertEqual(
            form(url="http://www.example.com"),
            u'<form action="http://www.example.com" method="post">'
        )
        self.assertEqual(
            form(url="http://www.example.com", method='GET'),
            u'<form action="http://www.example.com" method="GET">'
        )
        self.assertEqual(
            form('/test/edit/1'),
            u'<form action="/test/edit/1" method="post">'
        )

    def test_form_multipart(self):
        self.assertEqual(
            form(url='http://www.example.com', multipart=True),
            u'<form action="http://www.example.com" enctype="multipart/form-data" method="post">'
        )
        
    def test_hidden_field(self):
        self.assertEqual(
            hidden("id", 3),
            u'<input name="id" type="hidden" value="3" />'
        )

    def test_hidden_field_alt(self):
        self.assertEqual(
            hidden("id", '3'),
            u'<input name="id" type="hidden" value="3" />'
        )

    def test_password_field(self):
        self.assertEqual(
            password("password"), 
            u'<input name="password" type="password" />'
        )

    def test_radio_button(self):
        self.assertEqual(
            radio("people", "justin"),
            u'<input id="people_justin" name="people" type="radio" value="justin" />'
        )
        
        self.assertEqual(
            radio("num_people", 5),
            u'<input id="num_people_5" name="num_people" type="radio" value="5" />'
        )

        self.assertEqual(
            radio("num_people", 5),
            u'<input id="num_people_5" name="num_people" type="radio" value="5" />'
        )
        
        self.assertEqual(
            radio("gender", "m") + radio("gender", "f"),
            u'<input id="gender_m" name="gender" type="radio" value="m" /><input id="gender_f" name="gender" type="radio" value="f" />'
        )
        
        self.assertEqual(
            radio("opinion", "-1") + radio("opinion", "1"),
            u'<input id="opinion_-1" name="opinion" type="radio" value="-1" /><input id="opinion_1" name="opinion" type="radio" value="1" />'
        )

        self.assertEqual(
            radio("num_people", 5, checked=True),
            u'<input checked="checked" id="num_people_5" name="num_people" type="radio" value="5" />'
        )

    def test_submit(self):
        self.assertEqual(
            u'<input name="commit" type="submit" value="Save changes" />',
            submit("commit", "Save changes")
        )

    def test_text_area(self):
        self.assertEqual(
            textarea("aa", ""),
            u'<textarea name="aa"></textarea>'
        )
        self.assertEqual(
            textarea("aa", None),
            u'<textarea name="aa"></textarea>'
        )
        self.assertEqual(
            textarea("aa", "Hello!"),
            u'<textarea name="aa">Hello!</textarea>'
        )

    def test_text_area_size_string(self):
        self.assertEqual(
            textarea("body", "hello world", cols=20, rows=40),
            u'<textarea cols="20" name="body" rows="40">hello world</textarea>'
        )

    def test_text_field(self):
        self.assertEqual(
            text("title", ""),
            u'<input name="title" type="text" value="" />'
        )
        self.assertEqual(
            text("title", None),
            u'<input name="title" type="text" />'
        )
        self.assertEqual(
            text("title", "Hello!"),
            u'<input name="title" type="text" value="Hello!" />'
        )

    def test_text_field_class_string(self):
        self.assertEqual(
            text( "title", "Hello!", class_= "admin"),
            u'<input class="admin" name="title" type="text" value="Hello!" />'
        )

    def test_boolean_options(self):
        self.assertEqual(     
            checkbox("admin", 1, True, disabled = True, readonly="yes"),
            u'<input checked="checked" disabled="disabled" name="admin" readonly="readonly" type="checkbox" value="1" />'
        )
        self.assertEqual(
            checkbox("admin", 1, True, disabled = False, readonly = None),
            u'<input checked="checked" name="admin" type="checkbox" value="1" />'
        )

    
'''
class TestFormHelper(WebHelpersTestCase):
    def test_array_options_for_select(self):
        self.assertEqual(
            "<option value=\"&lt;Denmark&gt;\">&lt;Denmark&gt;</option>\n<option value=\"USA\">USA</option>\n<option value=\"Sweden\">Sweden</option>",
            options_for_select([ "<Denmark>", "USA", "Sweden" ]))

    def test_array_options_for_select_with_selection(self):
        self.assertEqual(
            "<option value=\"Denmark\">Denmark</option>\n<option selected=\"selected\" value=\"&lt;USA&gt;\">&lt;USA&gt;</option>\n<option value=\"Sweden\">Sweden</option>",
            options_for_select([ "Denmark", "<USA>", "Sweden" ], "<USA>"))

    def test_array_options_for_select_with_selection_array(self):
        self.assertEqual(
            "<option value=\"Denmark\">Denmark</option>\n<option selected=\"selected\" value=\"&lt;USA&gt;\">&lt;USA&gt;</option>\n<option selected=\"selected\" value=\"Sweden\">Sweden</option>",
            options_for_select([ "Denmark", "<USA>", "Sweden" ], [ "<USA>", "Sweden" ]))

    def test_array_options_for_string_include_in_other_string_bug_fix(self):
        self.assertEqual(
            "<option value=\"ruby\">ruby</option>\n<option selected=\"selected\" value=\"rubyonrails\">rubyonrails</option>",
            options_for_select([ "ruby", "rubyonrails" ], "rubyonrails"))
        self.assertEqual(
            "<option selected=\"selected\" value=\"ruby\">ruby</option>\n<option value=\"rubyonrails\">rubyonrails</option>",
            options_for_select([ "ruby", "rubyonrails" ], "ruby"))
        self.assertEqual(
            '<option selected="selected" value="ruby">ruby</option>\n<option value="rubyonrails">rubyonrails</option>\n<option></option>',
            options_for_select([ "ruby", "rubyonrails", None ], "ruby"))

    def test_hash_options_for_select_with_dict(self):
        self.assertEqual(
            "<option value=\"&lt;Kroner&gt;\">&lt;DKR&gt;</option>\n<option value=\"Dollar\">$</option>",
            options_for_select({ "$": "Dollar", "<DKR>": "<Kroner>" }))
        self.assertEqual(
            "<option value=\"&lt;Kroner&gt;\">&lt;DKR&gt;</option>\n<option selected=\"selected\" value=\"Dollar\">$</option>",
            options_for_select({ "$": "Dollar", "<DKR>": "<Kroner>" }, "Dollar"))
        self.assertEqual(
            "<option selected=\"selected\" value=\"&lt;Kroner&gt;\">&lt;DKR&gt;</option>\n<option selected=\"selected\" value=\"Dollar\">$</option>",
            options_for_select({ "$": "Dollar", "<DKR>": "<Kroner>" }, [ "Dollar", "<Kroner>" ]))

    def test_options_for_select_from_objects(self):
        class Something(object):
            select_name = "something"
            select_value = "The Something"
        class SomethingElse(object):
            select_name = "somethingelse"
            select_value = "The Something Else"
        def make_elem(x):
            return x.select_name
        def make_elem_both(x):
            return x.select_name, x.select_value
        self.assertEqual('<option value="something">something</option>\n<option value="somethingelse">somethingelse</option>',
                         options_for_select([Something(), SomethingElse()], function=make_elem))
        self.assertEqual('<option selected="selected" value="something">something</option>\n<option value="somethingelse">somethingelse</option>',
                         options_for_select([Something(), SomethingElse()], selected='something', function=make_elem))
        self.assertEqual('<option value="The Something">something</option>\n<option value="The Something Else">somethingelse</option>',
                         options_for_select([Something(), SomethingElse()], function=make_elem_both))
        self.assertEqual('<option selected="selected" value="The Something">something</option>\n<option value="The Something Else">somethingelse</option>',
                         options_for_select([Something(), SomethingElse()], 'The Something', make_elem_both))

    def test_options_for_select_from_dicts(self):
        def make_elem_name(x):
            return x['select_name']
        def make_elem_both(x):
            return x['select_name'], x['select_value']

        something = dict(select_name="something",
                         select_value="The Something")
        somethingelse = dict(select_name="somethingelse",
                         select_value="The Something Else")
        self.assertEqual('<option value="something">something</option>\n<option value="somethingelse">somethingelse</option>',
                         options_for_select([something, somethingelse], function=make_elem_name))
        self.assertEqual('<option selected="selected" value="something">something</option>\n<option value="somethingelse">somethingelse</option>',
                         options_for_select([something, somethingelse], selected='something', function=make_elem_name))
        self.assertEqual('<option value="The Something">something</option>\n<option value="The Something Else">somethingelse</option>',
                         options_for_select([something, somethingelse], function=make_elem_both))
        self.assertEqual('<option selected="selected" value="The Something">something</option>\n<option value="The Something Else">somethingelse</option>',
                         options_for_select([something, somethingelse], 'The Something', make_elem_both))
    

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
            "<option value=\"&lt;Kroner&gt;\">&lt;DKR&gt;</option>\n<option value=\"Dollar\">$</option>",
            options_for_select({ "$": "Dollar", "<DKR>": "<Kroner>" }))
        self.assertEqual(
            "<option value=\"&lt;Kroner&gt;\">&lt;DKR&gt;</option>\n<option value=\"Dollar\" selected=\"selected\">$</option>",
            options_for_select({ "$": "Dollar", "<DKR>": "<Kroner>" }, "Dollar"))
        self.assertEqual(
            "<option value=\"&lt;Kroner&gt;\" selected=\"selected\">&lt;DKR&gt;</option>\n<option value=\"Dollar\" selected=\"selected\">$</option>",
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
'''    

class TestLinkHelper(WebHelpersTestCase):
    def test_link_tag_with_query(self):
        self.assertEqual(u"<a href=\"http://www.example.com?q1=v1&amp;q2=v2\">Hello</a>", 
               link_to("Hello", "http://www.example.com?q1=v1&q2=v2"))
    
    def test_link_tag_with_query_and_no_name(self):
        self.assertEqual(u"<a href=\"http://www.example.com?q1=v1&amp;q2=v2\">http://www.example.com?q1=v1&amp;q2=v2</a>", 
               link_to(None, HTML.literal("http://www.example.com?q1=v1&amp;q2=v2")))
    
    def test_link_tag_with_custom_onclick(self):
        self.assertEqual(u"<a href=\"http://www.example.com\" onclick=\"alert('yay!')\">Hello</a>", 
               link_to("Hello", "http://www.example.com", onclick="alert('yay!')"))
    

class TestAssetTagHelper(WebHelpersTestCase):
    def test_auto_discovery_link_tag(self):
        self.assertEqual('<link href="http://feed.com/feed.xml" rel="alternate" title="RSS" type="application/rss+xml" />',
                         auto_discovery_link('http://feed.com/feed.xml'))
        self.assertEqual('<link href="http://feed.com/feed.xml" rel="alternate" title="ATOM" type="application/atom+xml" />',
                         auto_discovery_link('http://feed.com/feed.xml', feed_type='atom'))
        self.assertEqual('<link href="app.rss" rel="alternate" title="atom feed" type="application/atom+xml" />',
                         auto_discovery_link('app.rss', feed_type='atom', title='atom feed'))
        self.assertEqual('<link href="app.rss" rel="alternate" title="My RSS" type="application/rss+xml" />',
                         auto_discovery_link('app.rss', title='My RSS'))
        self.assertEqual('<link href="/app.rss" rel="alternate" title="" type="text/html" />',
                         auto_discovery_link('/app.rss', feed_type='text/html'))
        self.assertEqual('<link href="/app.html" rel="alternate" title="My RSS" type="text/html" />',
                         auto_discovery_link('/app.html', title='My RSS', feed_type='text/html'))
        
    def test_image(self):
        self.assertEqual('<img alt="Xml" src="/images/xml.png" />',
                         image('/images/xml.png', "Xml"))
        self.assertEqual('<img alt="Xml" src="/images/xml.png" />',
                         image('/images/xml.png', alt="Xml"))
        self.assertEqual('<img alt="" src="/images/xml.png" />',
                         image('/images/xml.png', ""))
        self.assertEqual('<img alt="" src="/images/xml.png" />',
                         image('/images/xml.png', None))
        self.assertEqual('<img alt="rss syndication" src="/images/rss.png" />',
                         image('/images/rss.png', 'rss syndication'))
        self.assertEqual('<img alt="Gold" height="70" src="gold.png" width="45" />',
                         image('gold.png', "Gold", height=70, width=45))
        self.assertEqual('<img alt="Edit Entry" height="10" src="/images/icon.png" width="16" />',
                         image("/images/icon.png", height=10, width=16, alt="Edit Entry"))
        self.assertEqual('<img alt="Icon" height="16" src="/icons/icon.gif" width="16" />',
                         image("/icons/icon.gif", "Icon", height=16, width=16))
        self.assertEqual('<img alt="Icon" src="/icons/icon.gif" width="16" />',
                         image("/icons/icon.gif", "Icon", width=16))

    def test_javascript_include_tag(self):
        self.assertEqual("""<script src="/javascripts/prototype.js" type="text/javascript"></script>\n<script src="/other-javascripts/util.js" type="text/javascript"></script>""",
                         javascript_link('/javascripts/prototype.js', '/other-javascripts/util.js'))
        self.assertEqual("""<script defer="defer" src="/js/pngfix.js" type="text/javascript"></script>""",
                         javascript_link('/js/pngfix.js', defer=True))

    def test_stylesheet_link_tag(self):
        self.assertEqual('<link href="/dir/file.css" media="all" rel="stylesheet" type="text/css" />',
                         stylesheet_link('/dir/file.css', media='all'))
        self.assertEqual('<link href="style.css" media="all" rel="stylesheet" type="text/css" />',
                         stylesheet_link('style.css', media='all'))
        self.assertEqual('<link href="/random.styles" media="screen" rel="stylesheet" type="text/css" />\n<link href="/css/stylish.css" media="screen" rel="stylesheet" type="text/css" />',
                         stylesheet_link('/random.styles', '/css/stylish.css'))


if __name__ == '__main__':
    suite = map(unittest.makeSuite, [
        TestFormTagHelper,
        TestFormHelper,
        TestFormOptionsHelper,
        TestLinkHelper,
        TestAssetTagHelper,
        ])
    for testsuite in suite:
        unittest.TextTestRunner(verbosity=1).run(testsuite)
