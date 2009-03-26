# -*- coding: utf-8 -*-
from util import WebHelpersTestCase
import unittest
from string24 import Template

from webhelpers.rails.text import *

class TestTextHelper(WebHelpersTestCase):
    
    def test_simple_format(self):
        self.assertEqual("<p></p>", simple_format(None))
        self.assertEqual("<p>crazy\n<br /> cross\n<br /> platform linebreaks</p>", simple_format("crazy\r\n cross\r platform linebreaks"))
        self.assertEqual("<p>A paragraph</p>\n\n<p>and another one!</p>", simple_format("A paragraph\n\nand another one!"))
        self.assertEqual("<p>A paragraph\n<br /> With a newline</p>", simple_format("A paragraph\n With a newline"))

    def test_auto_link_parsing(self):
        urls = [
            'http://www.rubyonrails.com',
            'http://www.rubyonrails.com:80',
            'http://www.rubyonrails.com/~minam',
            'https://www.rubyonrails.com/~minam',
            'http://www.rubyonrails.com/~minam/url%20with%20spaces',
            'http://www.rubyonrails.com/foo.cgi?something=here',
            'http://www.rubyonrails.com/foo.cgi?something=here&and=here',
            'http://www.rubyonrails.com/contact;new',
            'http://www.rubyonrails.com/contact;new%20with%20spaces',
            'http://www.rubyonrails.com/contact;new?with=query&string=params',
            'http://www.rubyonrails.com/~minam/contact;new?with=query&string=params',
            'http://en.wikipedia.org/wiki/Wikipedia:Today%27s_featured_picture_%28animation%29/January_20%2C_2007'
            ]
        for url in urls:
            self.assertEqual('<a href="%s">%s</a>' % (url, url),
                             auto_link(url))

    def test_auto_linking(self):
        raw_values = {
            'email_raw': 'david@loudthinking.com',
            'link_raw': 'http://www.rubyonrails.com',
            'link2_raw': 'www.rubyonrails.com',
            'link3_raw': 'http://manuals.ruby-on-rails.com/read/chapter.need_a-period/103#page281',
            'link4_raw': 'http://foo.example.com/controller/action?parm=value&p2=v2#anchor123',
            'link5_raw': 'http://foo.example.com:3000/controller/action',
            'link6_raw': 'http://foo.example.com:3000/controller/action+pack',
            'link7_raw': 'http://foo.example.com/controller/action?parm=value&p2=v2#anchor-123',
            'link8_raw': 'http://foo.example.com:3000/controller/action.html',
            'link9_raw': 'http://business.timesonline.co.uk/article/0,,9065-2473189,00.html'
            }

        result_values_templates = {
            'email_result':  '<a href="mailto:${email_raw}">${email_raw}</a>',
            'link_result':  '<a href="${link_raw}">${link_raw}</a>',
            'link_result_with_options':  '<a href="${link_raw}" target="_blank">${link_raw}</a>',
            'link2_result':  '<a href="http://${link2_raw}">${link2_raw}</a>',
            'link3_result':  '<a href="${link3_raw}">${link3_raw}</a>',
            'link4_result':  '<a href="${link4_raw}">${link4_raw}</a>',
            'link5_result':  '<a href="${link5_raw}">${link5_raw}</a>',
            'link6_result':  '<a href="${link6_raw}">${link6_raw}</a>',
            'link7_result':  '<a href="${link7_raw}">${link7_raw}</a>',
            'link8_result':  '<a href="${link8_raw}">${link8_raw}</a>',
            'link9_result':  '<a href="${link9_raw}">${link9_raw}</a>'
            }

        result_values = {}
        for k, v in result_values_templates.iteritems():
            result_values[k] = Template(v).substitute(raw_values)

        self.assertEqual("hello %(email_result)s" % result_values, auto_link("hello %(email_raw)s" % raw_values, 'email_addresses'))
        self.assertEqual("Go to %(link_result)s" % result_values, auto_link("Go to %(link_raw)s" % raw_values, 'urls'))
        self.assertEqual("Go to %(link_raw)s" % raw_values, auto_link("Go to %(link_raw)s" % raw_values, 'email_addresses'))
        self.assertEqual("Go to %(link_result)s and say hello to %(email_result)s" % result_values, auto_link("Go to %(link_raw)s and say hello to %(email_raw)s" % raw_values))
        self.assertEqual("<p>Link %(link_result)s</p>" % result_values, auto_link("<p>Link %(link_raw)s</p>" % raw_values))
        self.assertEqual("<p>%(link_result)s Link</p>" % result_values, auto_link("<p>%(link_raw)s Link</p>" % raw_values))
        self.assertEqual("<p>Link %(link_result_with_options)s</p>" % result_values, auto_link("<p>Link %(link_raw)s</p>" % raw_values, 'all', target='_blank'))
        self.assertEqual("Go to %(link_result)s." % result_values, auto_link("Go to %(link_raw)s." % raw_values))
        self.assertEqual("<p>Go to %(link_result)s, then say hello to %(email_result)s.</p>" % result_values, auto_link("<p>Go to %(link_raw)s, then say hello to %(email_raw)s.</p>" % raw_values))
        self.assertEqual("Go to %(link2_result)s" % result_values, auto_link("Go to %(link2_raw)s" % raw_values, 'urls'))
        self.assertEqual("Go to %(link2_raw)s" % raw_values, auto_link("Go to %(link2_raw)s" % raw_values, 'email_addresses'))
        self.assertEqual("<p>Link %(link2_result)s</p>" % result_values, auto_link("<p>Link %(link2_raw)s</p>" % raw_values))
        self.assertEqual("<p>%(link2_result)s Link</p>" % result_values, auto_link("<p>%(link2_raw)s Link</p>" % raw_values))
        self.assertEqual("Go to %(link2_result)s." % result_values, auto_link("Go to %(link2_raw)s." % raw_values))
        self.assertEqual("<p>Say hello to %(email_result)s, then go to %(link2_result)s.</p>" % result_values, auto_link("<p>Say hello to %(email_raw)s, then go to %(link2_raw)s.</p>" % raw_values))
        self.assertEqual("Go to %(link3_result)s" % result_values, auto_link("Go to %(link3_raw)s" % raw_values, 'urls'))
        self.assertEqual("Go to %(link3_raw)s" % raw_values, auto_link("Go to %(link3_raw)s" % raw_values, 'email_addresses'))
        self.assertEqual("<p>Link %(link3_result)s</p>" % result_values, auto_link("<p>Link %(link3_raw)s</p>" % raw_values))
        self.assertEqual("<p>%(link3_result)s Link</p>" % result_values, auto_link("<p>%(link3_raw)s Link</p>" % raw_values))
        self.assertEqual("Go to %(link3_result)s." % result_values, auto_link("Go to %(link3_raw)s." % raw_values))
        self.assertEqual("<p>Go to %(link3_result)s. seriously, %(link3_result)s? i think I'll say hello to %(email_result)s. instead.</p>" % result_values, auto_link("<p>Go to %(link3_raw)s. seriously, %(link3_raw)s? i think I'll say hello to %(email_raw)s. instead.</p>" % raw_values))
        self.assertEqual("<p>Link %(link4_result)s</p>" % result_values, auto_link("<p>Link %(link4_raw)s</p>" % raw_values))
        self.assertEqual("<p>%(link4_result)s Link</p>" % result_values, auto_link("<p>%(link4_raw)s Link</p>" % raw_values))
        self.assertEqual("<p>%(link5_result)s Link</p>" % result_values, auto_link("<p>%(link5_raw)s Link</p>" % raw_values))
        self.assertEqual("<p>%(link6_result)s Link</p>" % result_values, auto_link("<p>%(link6_raw)s Link</p>" % raw_values))
        self.assertEqual("<p>%(link7_result)s Link</p>" % result_values, auto_link("<p>%(link7_raw)s Link</p>" % raw_values))
        self.assertEqual("Go to %(link8_result)s" % result_values, auto_link("Go to %(link8_raw)s" % raw_values, 'urls'))
        self.assertEqual("Go to %(link8_raw)s" % raw_values, auto_link("Go to %(link8_raw)s" % raw_values, 'email_addresses'))
        self.assertEqual("<p>Link %(link8_result)s</p>" % result_values, auto_link("<p>Link %(link8_raw)s</p>" % raw_values))
        self.assertEqual("<p>%(link8_result)s Link</p>" % result_values, auto_link("<p>%(link8_raw)s Link</p>" % raw_values))
        self.assertEqual("Go to %(link8_result)s." % result_values, auto_link("Go to %(link8_raw)s." % raw_values))
        self.assertEqual("<p>Go to %(link8_result)s. seriously, %(link8_result)s? i think I'll say hello to %(email_result)s. instead.</p>" % result_values, auto_link("<p>Go to %(link8_raw)s. seriously, %(link8_raw)s? i think I'll say hello to %(email_raw)s. instead.</p>" % raw_values))
        self.assertEqual("Go to %(link9_result)s" % result_values, auto_link("Go to %(link9_raw)s" % raw_values, 'urls'))
        self.assertEqual("Go to %(link9_raw)s" % raw_values, auto_link("Go to %(link9_raw)s" % raw_values, 'email_addresses'))
        self.assertEqual("<p>Link %(link9_result)s</p>" % result_values, auto_link("<p>Link %(link9_raw)s</p>" % raw_values))
        self.assertEqual("<p>%(link9_result)s Link</p>" % result_values, auto_link("<p>%(link9_raw)s Link</p>" % raw_values))
        self.assertEqual("Go to %(link9_result)s." % result_values, auto_link("Go to %(link9_raw)s." % raw_values))
        self.assertEqual("<p>Go to %(link9_result)s. seriously, %(link9_result)s? i think I'll say hello to %(email_result)s. instead.</p>" % result_values, auto_link("<p>Go to %(link9_raw)s. seriously, %(link9_raw)s? i think I'll say hello to %(email_raw)s. instead.</p>" % raw_values))
        self.assertEqual("", auto_link(None))
        self.assertEqual("", auto_link(""))

    def test_cycle(self):
        self.assertEqual("one", cycle("one", "2", "3"))
        self.assertEqual("2", cycle("one", "2", "3"))
        self.assertEqual("3", cycle("one", "2", "3"))
        self.assertEqual("one", cycle("one", "2", "3"))
        self.assertEqual("2", cycle("one", "2", "3"))
        self.assertEqual("3", cycle("one", "2", "3"))

        self.assertEqual("3", cycle("3", "2", "one", name='ordered'))
        self.assertEqual("2", cycle("3", "2", "one", name='ordered'))
        self.assertEqual("one", cycle("3", "2", "one", name='ordered'))
        self.assertEqual("2", cycle("2", "3", "one", name='ordered'))
        self.assertEqual("3", cycle("2", "3", "one", name='ordered'))
        self.assertEqual("one", cycle("2", "3", "one", name='ordered'))

    def test_named_cycles(self):
        self.assertEqual(1, cycle(1, 2, 3, name="numbers"))
        self.assertEqual("red", cycle("red", "blue", name="colors"))
        self.assertEqual(2, cycle(1, 2, 3, name="numbers"))
        self.assertEqual("blue", cycle("red", "blue", name="colors"))
        self.assertEqual(3, cycle(1, 2, 3, name="numbers"))
        self.assertEqual("red", cycle("red", "blue", name="colors"))
  
    def test_default_named_cycle(self):
        self.assertEqual(1, cycle(1, 2, 3))
        self.assertEqual(2, cycle(1, 2, 3, name="default"))
        self.assertEqual(3, cycle(1, 2, 3))

    def test_reset_cycle(self):
        self.assertEqual(1, cycle(1, 2, 3))
        self.assertEqual(2, cycle(1, 2, 3))
        reset_cycle()
        self.assertEqual(1, cycle(1, 2, 3))

    def test_reset_unknown_cycle(self):
        reset_cycle("colors")
  
    def test_recet_named_cycle(self):
        self.assertEqual(1, cycle(1, 2, 3, name="numbers"))
        self.assertEqual("red", cycle("red", "blue", name="colors"))
        reset_cycle("numbers")
        self.assertEqual(1, cycle(1, 2, 3, name="numbers"))
        self.assertEqual("blue", cycle("red", "blue", name="colors"))
        self.assertEqual(2, cycle(1, 2, 3, name="numbers"))
        self.assertEqual("red", cycle("red", "blue", name="colors"))


    def test_counters(self):
        for i in range(1, 4):
            self.assertEqual(i, counter())
        reset_counter()
        for i in range(3):
            self.assertEqual(i, counter(start=0))
        reset_counter()
        for i in range(2, 5):
            self.assertEqual(i, counter(start=2))
        reset_counter()
        for i in range(1, -2, -1):
            self.assertEqual(i, counter(step=-1))

    def test_named_counters(self):
        for i in range(1, 4):
            self.assertEqual(i, counter(name="a"))
        for i in range(1, 4):
            self.assertEqual(i, counter(name="b"))
        for i in range(4, 7):
            self.assertEqual(i, counter(name="a"))

    def test_excerpt(self):
        self.assertEqual("...lo my wo...",
                         excerpt("hello my world", "my", 3))
        self.assertEqual("...is a beautiful morn...",
                         excerpt("This is a beautiful morning", "beautiful", 5))
        self.assertEqual("This is a...",
                         excerpt("This is a beautiful morning", "this", 5))
        self.assertEqual("...iful morning",
                         excerpt("This is a beautiful morning", "morning", 5))
        self.assertEqual('',
                         excerpt("This is a beautiful morning", "day"))

    def test_excerpt_with_regex(self):
        self.assertEqual('...is a beautiful! mor...',
                         excerpt('This is a beautiful! morning', 'beautiful', 5))
        self.assertEqual('...is a beautiful? mor...',
                         excerpt('This is a beautiful? morning', 'beautiful', 5))

    def test_excerpt_with_utf8(self):
        self.assertEqual(u"...ﬃciency could not be ...",
                         excerpt(u"That's why eﬃciency could not be helped", 'could', 8))


    def test_highlighter(self):
        self.assertEqual("This is a <strong class=\"highlight\">beautiful</strong> morning",
                         highlight("This is a beautiful morning", "beautiful"))
        self.assertEqual(
            "This is a <strong class=\"highlight\">beautiful</strong> morning, but also a <strong class=\"highlight\">beautiful</strong> day",
            highlight("This is a beautiful morning, but also a beautiful day", "beautiful"))
        self.assertEqual("This is a <b>beautiful</b> morning, but also a <b>beautiful</b> day",
                         highlight("This is a beautiful morning, but also a beautiful day",
                                   "beautiful", r'<b>\1</b>'))
        self.assertEqual("This text is not changed because we supplied an empty phrase",
                         highlight("This text is not changed because we supplied an empty phrase",
                                   None))

    def test_highlighter_with_regex(self):
        self.assertEqual("This is a <strong class=\"highlight\">beautiful!</strong> morning",
                     highlight("This is a beautiful! morning", "beautiful!"))

        self.assertEqual("This is a <strong class=\"highlight\">beautiful! morning</strong>",
                     highlight("This is a beautiful! morning", "beautiful! morning"))

        self.assertEqual("This is a <strong class=\"highlight\">beautiful? morning</strong>",
                     highlight("This is a beautiful? morning", "beautiful? morning"))

    def test_strip_links(self):
        self.assertEqual("on my mind", strip_links("<a href='almost'>on my mind</a>"))
        self.assertEqual("on my mind", strip_links("<A href='almost'>on my mind</A>"))
        self.assertEqual("on my mind\nall day long",
                         strip_links("<a href='almost'>on my mind</a>\n<A href='almost'>all day long</A>"))

    def test_truncate(self):
        self.assertEqual("Hello World!", truncate("Hello World!", 12))
        self.assertEqual("Hello Wor...", truncate("Hello World!!", 12))

    def test_textilize(self):
        self.assertEqual('<h1>This is a test of textile</h1>\n\n<p>Paragraph</p>\n\n<p>Another paragraph</p>\n\n<ul>\n<li>Bullets</li>\n</ul>',
                         textilize("h1. This is a test of textile\n\nParagraph\n\nAnother paragraph\n\n* Bullets"))

    def test_markdown(self):
        markdown_text = """
Introduction
------------

Markdown is a text-to-HTML conversion tool for web writers.

Acknowledgements <a id="acknowledgements" />
----------------

[Michel Fortin][] has ported to Markdown to PHP.
        """
        self.assertEqual('\n\n<h2>Introduction</h2>\n<p>Markdown is a text-to-HTML conversion tool for web writers.\n</p>\n\n<h2>Acknowledgements <a id="acknowledgements" /></h2>\n<p>[Michel Fortin][] has ported to Markdown to PHP.\n</p>\n\n\n',
                         markdown(markdown_text))

if __name__ == '__main__':
    suite = [unittest.makeSuite(TestTextHelper)]
    for testsuite in suite:
        unittest.TextTestRunner(verbosity=1).run(testsuite)
