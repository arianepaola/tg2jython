from unittest import TestCase
from itertools import count
import tw
from tw.core.testutil import WidgetMixin, WidgetTestCase
from tw.api import (Widget, JSLink, CSSLink, CSSSource, JSSource, IECSSLink,
                    IECSSSource, IEJSLink, IEJSSource, retrieve_resources,
                    locations, JSMixin, CSSMixin, inject_resources)

class TestJSLink(WidgetMixin, TestCase):
    TestWidget = JSLink
    widget_kw = {
        'modname': 'tw', 
        'filename': 'Test.js',
        }

    def test_link_generated_correctly(self):
        self.assertInOutput(["<script","javascript","/tw/Test.js"])

class TestCSSLink(WidgetMixin, TestCase):
    TestWidget = CSSLink
    widget_kw = {
        'modname': 'tw', 
        'filename': 'Test.css',
        'media': 'printer'
        }

    def test_link_generated_correctly(self):
        self.assertInOutput([
            "<link", "text/css", "/tw/Test.css", 'media="printer"',
            ])




class TestCSSSource(WidgetMixin, TestCase):
    TestWidget = CSSSource
    widget_kw = {
        'src': 'foobarfoofoo',
        'media': 'printer',
        }

    def test_source_generated_correctly(self):
        self.assertInOutput([
            "<style", "text/css", "foobarfoofoo", 'media="printer"',
            ])




class TestJSSSource(WidgetMixin, TestCase):
    TestWidget = JSSource
    widget_kw = {
        'src': 'foobarfoofoo',
        }

    def test_source_generated_correctly(self):
        self.assertInOutput(["<script", "text/javascript", "foobarfoofoo"])


class TestJavascriptIsCollected(TestCase):

    def test_order_is_preserved_in_js(self):
        js = [JSSource(src="source%d"%i) for i in xrange(5)]
        w = Widget(javascript=js)
        self.failUnlessEqual(
            [j.src for j in w.retrieve_resources()['head']],
            ["source%d"%i for i in xrange(5)]
            )

    def test_no_duplicates_in_js(self):
        js = ([JSSource(src="source%d"%i) for i in xrange(5)] +
              [JSSource(src="source%d"%i) for i in xrange(2,10)])
        w = Widget(javascript=js)
        self.failUnlessEqual(
            [j.src for j in w.retrieve_resources()['head']],
            ["source%d"%i for i in xrange(10)]
            )
        self.failUnlessEqual(len(w.retrieve_resources()['head']), 10)

    def test_js_is_collected_from_JSSource(self):
        w = JSSource(src="foo")
        self.failUnless(w in w.retrieve_resources()['head'])

    def test_js_dependencies_are_collected(self):
        d1 = JSSource(src="d1")
        d2 = JSSource(src="d2")
        w = JSSource(src="foo", javascript=[d1,d2])
        js = w.retrieve_resources()['head']
        self.failUnlessEqual(js[0].src, 'd1')
        self.failUnlessEqual(js[1].src, 'd2')
        self.failUnlessEqual(js[2].src, 'foo')


class TestCSSIsCollected(TestCase):
    def test_order_is_preserved_in_css(self):
        css = [CSSSource(src="source%d"%i) for i in xrange(5)]
        w = Widget(css=css)
        self.failUnlessEqual(
            [c.src for c in w.retrieve_resources()['head']],
            ["source%d"%i for i in xrange(5)]
            )


    def test_no_duplicates_in_css(self):
        css = ([CSSSource(src="source%d"%i) for i in xrange(5)] +
               [CSSSource(src="source%d"%i) for i in xrange(2,10)])
        w = Widget(css=css)
        self.failUnlessEqual(
            [c.src for c in w.retrieve_resources()['head']],
            ["source%d"%i for i in xrange(10)]
            )

    def test_css_is_collected_from_children(self):
        c = count()
        children = [
            Widget(css=[CSSSource(src='source%d'% c.next()) for i in xrange(5)])
                for i in xrange(5)
            ]
        p = Widget(children=children)
        self.assertEqual(len(p.retrieve_resources()['head']), 25)
        

class TestResourcesAreCollected(TestCase):
    def test_order_is_preserved_in_css_and_css_is_in_head(self):
        css = [CSSSource(src="source%d"%i) for i in xrange(5)]
        w = Widget(css=css)
        resources = w.retrieve_resources()
        self.failUnlessEqual(
            [c.src for c in resources[locations.head]],
            ["source%d"%i for i in xrange(5)]
            )

    def test_resources_are_classified_correctly(self):
        js = [JSSource(src="js%d-%s"%(i,l), location=l) 
            for l in locations for i in xrange(5)]
        w = Widget(javascript=js)
        resources = w.retrieve_resources()
        for l in locations:
            self.failUnlessEqual(
                [r.src for r in resources[l]], 
                ["js%d-%s"%(i,l) for i in xrange(5)]
                )

    def test_resources_are_collected_from_children(self):
        c = count()
        children = [
            Widget(css=[CSSSource(src='source%d'% c.next()) for i in xrange(5)])
                for i in xrange(5)
            ]
        p = Widget(children=children)
        self.assertEqual(len(p.retrieve_resources()[locations.head]), 25)

    def test_resource_dependencies_are_collected(self):
        c1 = CSSSource(src="c1")
        c2 = CSSSource(src="c2")
        j1 = JSSource(src="d1")
        j2 = JSSource(src="d2")
        js = JSSource(src="js", css=[c1,c2], javascript=[j1,j2])
        css = CSSSource(src="css", css=[c1,c2], javascript=[j1,j2])
        w = Widget(javascript=[js], css=[css])
        head_resources = w.retrieve_resources()['head']
        js = filter(lambda s: isinstance(s, JSMixin), head_resources)
        css = filter(lambda s: isinstance(s, CSSMixin), head_resources)
        self.failUnlessEqual(len(css), 3)
        self.failUnlessEqual(len(js), 3)

class TestResourcesAreCollectedWith_retrieve_resources(TestCase):
    def test_order_is_preserved_in_css_and_css_is_in_head(self):
        css = [CSSSource(src="source%d"%i) for i in xrange(5)]
        w = Widget(css=css)
        resources = retrieve_resources(w)
        self.failUnlessEqual(
            [c.src for c in resources[locations.head]],
            ["source%d"%i for i in xrange(5)]
            )

    def test_resources_are_classified_correctly(self):
        js = [JSSource(src="js%d-%s"%(i,l), location=l) 
            for l in locations for i in xrange(5)]
        w = Widget(javascript=js)
        resources = retrieve_resources(w)
        for l in locations:
            self.failUnlessEqual(
                [r.src for r in resources[l]], 
                ["js%d-%s"%(i,l) for i in xrange(5)]
                )

    def test_resources_are_collected_from_children(self):
        c = count()
        children = [
            Widget(css=[CSSSource(src='source%d'% c.next()) for i in xrange(5)])
                for i in xrange(5)
            ]
        p = Widget(children=children)
        self.assertEqual(len(retrieve_resources(p)[locations.head]), 25)

    def test_resources_are_collected_from_unknown(self):
        resources = retrieve_resources(None)
        self.assert_(not resources)

    def test_resources_are_collected_from_list(self):
        js = [JSSource(src="source%d"%i) for i in xrange(15)]

        widgets = [
            Widget(javascript=js[:5]),
            Widget(javascript=js[5:10]),
            Widget(javascript=js[10:]),
            ]
        resources = retrieve_resources(widgets)
        self.failUnlessEqual(
            [c.src for c in resources[locations.head]],
            ["source%d"%i for i in xrange(15)]
            )

    def test_resources_are_collected_from_dict(self):
        js = [
            JSSource(src="source%d"%i, location=locations.head) 
                for i in xrange(15)
            ]

        widgets = {
            '1': Widget(javascript=js[:5]),
            '2': Widget(javascript=js[5:10]),
            '3': Widget(javascript=js[10:]),
            }
        resources = retrieve_resources(widgets)
        self.assertEqual(len(retrieve_resources(widgets)[locations.head]), 15)
    
    def test_no_resources_return_empty_dict(self):
        self.failUnlessEqual(
            retrieve_resources(Widget(children=[Widget()]) for x in xrange(2)),
            {}
            )

class TestIECSSLink(WidgetTestCase):
    widget = IECSSLink(modname="tw", filename="foo")

    def test_wo_version(self):
        self.assertInOutput(["<!--[if IE]>","<![endif]-->","<link","text/css"])

    def test_simple_version(self):
        self.assertInOutput(["<!--[if IE 5]>", "<![endif]-->"], version=5)

    def test_full_version(self):
        self.assertInOutput("<!--[if IE gt 5]>", version=">5")
        self.assertInOutput("<!--[if IE gt 5]>", version="gt 5")
        self.assertInOutput("<!--[if IE gte 5]>", version=">=5")
        self.assertInOutput("<!--[if IE gte 5]>", version="gte 5")
        self.assertInOutput("<!--[if IE lt 5]>", version="<5")
        self.assertInOutput("<!--[if IE lt 5]>", version="lt 5")
        self.assertInOutput("<!--[if IE lte 5]>", version="<=5")
        self.assertInOutput("<!--[if IE lte 5]>", version="lte 5")

class TestIECSSSource(WidgetTestCase):
    widget = IECSSSource("#topbar { float: left;}")

    def test_wo_version(self):
        self.assertInOutput(["<!--[if IE]>", "<![endif]-->", "<style"])

    def test_simple_version(self):
        self.assertInOutput(["<!--[if IE 5]>", "<![endif]-->"], version=5)

    def test_full_version(self):
        self.assertInOutput("<!--[if IE gt 5]>", version=">5")
        self.assertInOutput("<!--[if IE gt 5]>", version="gt 5")
        self.assertInOutput("<!--[if IE gte 5]>", version=">=5")
        self.assertInOutput("<!--[if IE gte 5]>", version="gte 5")
        self.assertInOutput("<!--[if IE lt 5]>", version="<5")
        self.assertInOutput("<!--[if IE lt 5]>", version="lt 5")
        self.assertInOutput("<!--[if IE lte 5]>", version="<=5")
        self.assertInOutput("<!--[if IE lte 5]>", version="lte 5")

class TestIEJSLink(WidgetTestCase):
    widget = IEJSLink(modname="tw", filename="foo")

    def test_wo_version(self):
        self.assertInOutput(
            ["<!--[if IE]>", "<![endif]-->", "<script", "text/javascript"]
            )

    def test_simple_version(self):
        self.assertInOutput(["<!--[if IE 5]>", "<![endif]-->"], version=5)

    def test_full_version(self):
        self.assertInOutput("<!--[if IE gt 5]>", version=">5")
        self.assertInOutput("<!--[if IE gt 5]>", version="gt 5")
        self.assertInOutput("<!--[if IE gte 5]>", version=">=5")
        self.assertInOutput("<!--[if IE gte 5]>", version="gte 5")
        self.assertInOutput("<!--[if IE lt 5]>", version="<5")
        self.assertInOutput("<!--[if IE lt 5]>", version="lt 5")
        self.assertInOutput("<!--[if IE lte 5]>", version="<=5")
        self.assertInOutput("<!--[if IE lte 5]>", version="lte 5")

class TestIEJSSource(WidgetTestCase):
    widget = IEJSSource("function() {};")

    def test_wo_version(self):
        self.assertInOutput(["<!--[if IE]>", "<![endif]-->", "<script"])

    def test_simple_version(self):
        self.assertInOutput(["<!--[if IE 5]>", "<![endif]-->"], version=5)

    def test_full_version(self):
        self.assertInOutput("<!--[if IE gt 5]>", version=">5")
        self.assertInOutput("<!--[if IE gt 5]>", version="gt 5")
        self.assertInOutput("<!--[if IE gte 5]>", version=">=5")
        self.assertInOutput("<!--[if IE gte 5]>", version="gte 5")
        self.assertInOutput("<!--[if IE lt 5]>", version="<5")
        self.assertInOutput("<!--[if IE lt 5]>", version="lt 5")
        self.assertInOutput("<!--[if IE lte 5]>", version="<=5")
        self.assertInOutput("<!--[if IE lte 5]>", version="lte 5")

class TestExternalLinks(TestCase):
    def test_jslink(self):
        output = JSLink(link="http://google.com/mapreduce.js").render()
        self.failUnless('src="http://google.com/mapreduce.js"' in output,
                        output)

    def test_csslink(self):
        output = CSSLink(link="http://google.com/mapreduce.css").render()
        self.failUnless('href="http://google.com/mapreduce.css"' in output,
                        output)

class TestResourceRegistry(WidgetTestCase):
    template = "<html><head></head><body></body></html>"
    def test_inject_resources(self):
        inj = inject_resources(self.template)
        self.failUnless('example.com' not in inj)
        JSLink(link="http://example.com").inject()
        inj = inject_resources(self.template)
        self.failUnless('example.com' in inj)
        self.failUnless(not tw.framework.pop_resources())

    def test_resources_are_popped(self):
        JSLink(link="http://example.com").inject()
        self.failUnless(tw.framework.pop_resources())
        self.failUnless(not tw.framework.pop_resources())

    def test_resources_are_popped_after_injecton(self):
        JSLink(link="http://example.com").inject()
        inj = inject_resources(self.template)
        self.failUnless('example.com' in inj)
        inj = inject_resources(self.template)
        self.failUnless('example.com' not in inj)
