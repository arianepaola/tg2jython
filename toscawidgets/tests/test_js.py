from unittest import TestCase
from tw.core.testutil import WidgetTestCase
from tw.api import Widget, JSSource, js_function, js_callback
from tw.core.resources import dynamic_js_calls

a_js_func = js_function('a_js_func')

class TestStaticCalls(WidgetTestCase):

    class TestWidget(Widget):

        def __init__(self, *args, **kw):
            self.add_call(
                a_js_func(self.id, "This is a test")
                )

        def update_params(self, d):
            Widget.update_params(self,d)
            self.add_call(
                a_js_func(self.id, "This shouldn't be possible")
                )
        
    def test_calls_are_added(self):
        self.failUnless("This is a test" in str(self.widget._js_calls[0]))

    def XXXtest_dynamic_calls_not_possible(self):
        #XXX: This is no loner a limitation
        self.failUnlessRaises(TypeError, self.widget.update_params, {})

class TestDynamicCalls(WidgetTestCase):
    def setUp(self):
        super(TestDynamicCalls, self).setUp()
        try:
            del Widget()._calls_for_request
        except AttributeError:
            pass

    class TestWidget(Widget):
        params = "test", "call_location"
        #XXX: Widget needs a template or else update_params will never be called
        #XXX: branches/widget_base_refactoring fixes this
        #template = "$value"
        call_location = "bodybottom"

        def update_params(self, d):
            Widget.update_params(self,d)
            self.add_call(a_js_func(d.test), d.call_location)
        
    def XXXtest_dynamic_calls_widget_is_included_in_widget_resources(self):
        #XXX Implementation has changed and this test makes no sense as-is
        widget_js = self.widget.retrieve_javascript()
        self.failUnless(dynamic_js_calls in widget_js)

    def test_dynamic_calls_possible(self):
        self.assertInDynamicCalls("Foo", test="Foo")

    def test_dynamic_calls_head(self):
        self.assertInDynamicCalls("headcall", test="headcall", location="head",
                                  call_location="head")

class TestChainedCalls(TestCase):
    def test_can_chain_calls(self):
        jQuery = js_function('jQuery')
        cb = js_callback('make_async')
        call = jQuery('a .async').click(cb).foo().bar()
        expected = 'jQuery("a .async").click(make_async).foo().bar()'
        self.failUnlessEqual(str(call), expected)
    
    def test_attr_mixed_in_chain_call(self):
        proto = js_function('$')
        iframe = js_callback('window.frames.my_iframe')
        call = proto('my_component').ajax.load_in(iframe)
        expected = '$("my_component").ajax.load_in(window.frames.my_iframe)'
        self.failUnlessEqual(str(call), expected)

    def test_last_element_should_be_called(self):
        proto = js_function('$')
        call = proto('my_component').ajax
        try:
            str(call)
            assert False, 'Last element isn\'t a call, shouldn\'t work!'
        except TypeError, e:
            # just to be sure it's the type error we were expecting
            assert e.args[0] == 'Last element in the chain has to be called'

