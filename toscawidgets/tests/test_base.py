from tw.core import Widget, WidgetRepeater, WidgetsList, Child, WidgetBunch
from tw.core.util import RequestLocalDescriptor, lazystring
from tw.core.testutil import WidgetTestCase, WidgetRequireTestCase
from unittest import TestCase


class TestWidgetWithDefault(WidgetTestCase):
    class TestWidget(Widget):
        template = "$value"
        default = 2

    def test_default_is_respected(self):
        self.assertInOutput("2")

class TestWidgetWithCallableDefault(WidgetTestCase):
    class TestWidget(Widget):
        template = "$value"
        default = lambda s: 2

    def test_default_is_respected(self):
        self.assertInOutput("2")

class TestMutableTemplateVarsNotClobbered(WidgetRequireTestCase):
    require = ["Genshi"]
    class TestWidget(Widget):
        params = "lst dct".split()
        template = """
        <div
            xmlns="http://www.w3.org/1999/xhtml"
            xmlns:py="http://genshi.edgewall.org/" 
            py:attrs="dct">
            <span py:for="i in lst" py:replace="i" />
        </div>"""
        engine_name = 'genshi'
        lst = []
        dct = {}
        def __init__(self, *args, **kw):
            self.lst.append('1')
            self.dct.update({'foo':'bar'})
        def update_params(self,d):
            Widget.update_params(self,d)
            d['lst'].append('2')
            d['dct'].update({'bar':'foo'})

    widget_kw = dict(dct={},lst=[])




    def test_class_and_args_not_modified_on_init(self):
        w = self.widget
        W = self.TestWidget
        self.assertEquals(self.widget_kw['dct'], {})
        self.assertEquals(self.widget_kw['lst'], [])
        self.assertEquals(W.dct, {})
        self.assertEquals(W.lst, [])
        self.assertEquals(w.lst, ['1'])
        self.assertEquals(w.dct, {'foo':'bar'})

    def test_instance_and_args_not_modified_on_display(self):
        dct = {'spam':'eggs'}
        lst = ['3']
        w = self.widget
        W = self.TestWidget

        self.assertInOutput(['spam="eggs"','3'], lst=lst, dct=dct)
        self.assertEquals(W.dct, {})
        self.assertEquals(W.lst, [])
        self.assertEquals(w.lst, ['1'])
        self.assertEquals(w.dct, {'foo':'bar'})
        #XXX: Should Widget make a copy of mutable args passed to display?
        #self.assertEquals(lst, ['3'])
        #self.assertEquals(dct, {'spam':'eggs'})






class TestWidgetsList(TestCase):
    def test_order_is_preserved(self):
        class TestList(WidgetsList):
            foo = Widget()
            bar = Widget()
            spam = Widget()
            eggs = Widget()
        names = [w.id for w in TestList()]
        self.failUnlessEqual(names, "foo bar spam eggs".split())





class TestParams(WidgetRequireTestCase):
    class TestWidget(Widget):
        params = ["foo1", "foo2", "foo3", "bar"]
        foo1 = staticmethod(lambda: 'foo')
        foo2 = staticmethod(lambda foo='foo': foo)
        def foo3(self):
            return 'foo'
        template = """<h1>${foo1}</h1><h2>${foo2}</h2><h3>${foo3}</h3>"""

    def test_callable_default_params(self):
        self.assertInOutput(['<h1>foo</h1>', '<h2>foo</h2>'])

    def XXXtest_callable_display_overriden_params(self):
        #XXX This behaviour is deprecated, there's not reason to pass
        #    a callable at display and incurs in a preformance penalty
        self.assertInOutput(
            ['<h1>bar</h1>', '<h2>foo</h2>'], foo1=lambda: 'bar')

    def test_method_as_param(self):
        self.assertInOutput('<h3>foo</h3>')

    def test_params_are_set_to_None_by_default(self):
        self.failUnless(hasattr(self.widget, 'bar'))
        self.failUnless(self.widget.bar is None)





class TestWidgetRepeater(WidgetTestCase):
    class TestWidget(WidgetRepeater):
        class Repeated(Widget):
            template = """<input id="${id}" />"""
        max_repetitions = 5
        widget = Repeated()

    def test_render(self):
        self.assertInOutput('input')
        
    def test_correct_ids(self):
        reps = 5
        self.assertInOutput(
            ['test-%d'%i for i in xrange(reps)], repetitions=reps
            )

    def test_limit_repetitions(self):
        reps = 3
        self.assertInOutput(
            ['test-%d'%i for i in xrange(reps)], repetitions=reps
            )
        self.assertNotInOutput(
            ['foo-%d'%i for i in xrange(reps, 5)], repetitions=reps
            )






class TestWidgetRepeaterNestedRepeated(WidgetRequireTestCase):
    require = ["Genshi"]
    class TestWidget(Widget):
        template = """
        <div>${children.fs.display(value_for('fs'), **args_for('fs'))}</div> """
        engine_name = 'genshi'

        class Repeater(WidgetRepeater):
            max_repetitions = 5
            repetitions = 5

            class Fieldset(Widget):
                params=["legend"]
                class Inner(Widget):
                    params = ["test"]
                    template = """
                        <input id="${id}" value="${value}" test="${test}" />
                        """
                children = [Inner('foo'),Inner('bar')]
                engine_name = 'genshi'
                template = """
                <fieldset id="${id}" legend="${legend}"
                    xmlns="http://www.w3.org/1999/xhtml"
                    xmlns:py="http://genshi.edgewall.org/">
                    <span py:for="c in children" 
                          py:replace="c.display(value_for(c), **args_for(c))" />
                </fieldset>"""
            widget = Fieldset
        children = [Repeater('fs')]
        #children = [Child(Repeater, 'fs')]

    def test_widget_is_built_correctly(self):
        w = self.widget
        self.assertEqual(len(w.c), 1)
        self.assertEqual(len(w.c[0].children), 5)
        for c in w.c[0].children:
            self.assertEqual(len(c.children), 2)

    def test_render(self):
        self.assertInOutput('input')
        
    def test_correct_ids(self):
        reps = 5
        self.assertInOutput(
            ['fs-%d_bar'%i for i in xrange(reps)] +
            ['fs-%d_foo'%i for i in xrange(reps)] , 
            child_args={'fs':{'repetitions':reps}}
            )

    def test_limit_repetitions(self):
        reps = 3
        self.assertInOutput(
            ['fs-%d_bar'%i for i in xrange(reps)] +
            ['fs-%d_foo'%i for i in xrange(reps)] , 
            child_args={'fs':{'repetitions':reps}}
            )
        self.assertNotInOutput(
            ['fs-%d_bar'%i for i in xrange(reps,5)] +
            ['fs-%d_foo'%i for i in xrange(reps,5)] , 
            child_args={'fs':{'repetitions':reps}}
            )

    def test_children_receive_values(self):
        class Obj(object):
            def __init__(self, foo, bar):
                self.foo = foo
                self.bar = bar
        values = [Obj('alberto%d'%i, 'gggg%d'%i) for i in xrange(5)]
        self.assertInOutput(
            ['alberto%d'%i for i in xrange(5)] + 
            ['gggg%d'%i for i in xrange(5)], dict(fs=values)
            )

    def test_children_receive_args(self):
        child_args = dict(fs=dict(child_args=[dict(child_args=dict(
            foo={'test':'foo%d'%i}, 
            bar={'test':'bar%d'%i}
            )) for i in xrange(5)]))
        self.assertInOutput(
            ['foo%d'%i for i in xrange(5)] +
            ['bar%d'%i for i in xrange(5)], child_args=child_args)


    def test_children_receive_args_dotted_id(self):
        child_args = {}
        args = [{
            'fs-%d.foo'%i : {'test':'foo%d'%i},
            'fs-%d.bar'%i : {'test':'bar%d'%i},
            } for i in xrange(5)]
        map(child_args.update, args)
        self.assertInOutput(
            ['foo%d'%i for i in xrange(5)] +
            ['bar%d'%i for i in xrange(5)], child_args=child_args)

    def test_children_receive_args_dotted_id_outside_child_args(self):
        child_args = {}
        args = [{
            'fs-%d.foo'%i : {'test':'foo%d'%i},
            'fs-%d.bar'%i : {'test':'bar%d'%i},
            } for i in xrange(5)]
        map(child_args.update, args)
        self.assertInOutput(
            ['foo%d'%i for i in xrange(5)] +
            ['bar%d'%i for i in xrange(5)], **child_args)

    def test_first_child_can_receive_in_dotted_args_outside_child_args(self):
        args = [{'.fs-%d'%i:{'legend':'Fieldset-%d'%i}} for i in xrange(5)]
        child_args = {}
        map(child_args.update, args)
        self.assertInOutput(['Fieldset-%d'%i for i in xrange(5)], **child_args)

    def test_children_can_receive_args_by_key(self):
        children = self.widget.c.fs.children
        args = [{c.key:{'legend':'Fieldset-%d'%i}} for i,c in enumerate(children)]
        child_args = {}
        map(child_args.update, args)
        self.assertInOutput(['Fieldset-%d'%i for i in xrange(5)], **child_args)

class SomeFieldset(Widget):
    engine_name = "genshi"
    params = ["legend"]
    template = """
    <fieldset id="${id}" legend="${legend}"
        xmlns="http://www.w3.org/1999/xhtml"
        xmlns:py="http://genshi.edgewall.org/">
        <span py:for="c in children" 
              py:replace="c.display(value_for(c), **args_for(c))" />
    </fieldset>"""

class DoubleNestedRepeated(SomeFieldset):
    children = [WidgetRepeater("fsA",
        widget=SomeFieldset(children=[WidgetRepeater("fsB",
            widget=SomeFieldset(),
            repetitions=2
            )]),
        repetitions=2
        )]
dlr = DoubleNestedRepeated("test")

class TestDoubleNestedRepeatedInner0(WidgetRequireTestCase):
    require = ["Genshi"]
    widget = dlr.children[0].children[0]
    def test_ids_are_correct(self):
        expected = ["test_fsA-0_fsB-%d" % i for i in range(2)]
        self.assertInOutput(expected)

class TestDoubleNestedRepeatedInner1(WidgetRequireTestCase):
    require = ["Genshi"]
    widget = dlr.children[0].children[1]
    def test_ids_are_correct(self):
        expected = ["test_fsA-1_fsB-%d" % i for i in range(2)]
        self.assertInOutput(expected)

class TestDoubleNestedRepeatedOuter(WidgetRequireTestCase):
    require = ["Genshi"]
    widget = dlr
    def test_ids_are_correct(self):
        expected = ["test_fsA-%d_fsB-%d" % (i,j)
                    for i in range(2) for j in range(2)]
        self.assertInOutput(expected)

class TestArgsForChilds(WidgetRequireTestCase):
    require = ["Genshi"]
    class TestWidget(Widget):
        class Inner(Widget):
            params = ["test"]
            template = """<p id="${id}">${test}</p>"""
        template = """<ul
            xmlns="http://www.w3.org/1999/xhtml"
            xmlns:py="http://genshi.edgewall.org/">
        <li py:for="c in children" py:replace="c.display(**args_for(c))" />
        </ul>
        """
        engine_name = 'genshi'
        children = [Inner('foo'),Inner('bar')]

    def test_children_receive_args(self):
        self.assertInOutput(
            ['alberto','gggg'], 
            child_args=dict(foo={'test':'alberto'}, bar={'test':'gggg'})
            )




class TestValueForChilds(WidgetRequireTestCase):
    require = ["Genshi"]
    class TestWidget(Widget):
        class Inner(Widget):
            template = """<p id="${id}">${value}</p>"""
        template = """<ul
            xmlns="http://www.w3.org/1999/xhtml"
            xmlns:py="http://genshi.edgewall.org/">
        <li py:for="c in children" py:replace="c.display(value_for(c))" />
        </ul>
        """
        engine_name = 'genshi'
        children = [Inner('foo'),Inner('bar')]

    def test_children_receive_value(self):
        class Value:
            foo = 'alberto'
            bar = 'gggg'
        self.assertInOutput(['alberto','gggg'], Value())

class TestChildrenAreCollectedFromBases(WidgetTestCase):
    class BaseWidget(Widget):
        children = [Widget('foo')]
    class TestWidget(BaseWidget):
        pass
    
    def test_are_collected(self):
        self.failUnless(hasattr(self.widget.c, 'foo'))

class TestDictInUpdateParamsIsABunch(WidgetTestCase):
    class TestWidget(Widget):
        template = "$foo"
        def update_params(self,d):
            Widget.update_params(self,d)
            d.foo = 'bar'
    
    def test_is_bunch(self):
        self.assertInOutput('bar')

class TestTemplate(WidgetTestCase):
    class TestWidget(Widget):
        template = "$foo"
        def update_params(self,d):
            Widget.update_params(self,d)
            d.foo = 'bar'

    def test_at_class_template(self):
        self.assertInOutput('bar')

    def test_at_display_template(self):
        self.assertInOutput('isbar', template="is$foo")

class TestRequestLocalDescriptorNoDeafult(WidgetTestCase):
    class TestWidget(Widget):
        foo = RequestLocalDescriptor('foo')

    def test_can_be_set(self):
        self.widget.foo = 'bar'
        self.failUnlessEqual(self.widget.foo, 'bar')

    def test_can_be_del(self):
        self.widget.foo = 'bar'
        del self.widget.foo
        self.assertRaises(AttributeError, getattr, self.widget, 'foo')

    def test_can_be_del_resetted(self):
        self.widget.foo = 'bar'
        del self.widget.foo
        self.assertRaises(AttributeError, getattr, self.widget, 'foo')
        self.widget.foo = 'bar'
        self.failUnlessEqual(self.widget.foo, 'bar')

class TestRequestLocalDescriptorDeafult(WidgetTestCase):
    class TestWidget(Widget):
        foo = RequestLocalDescriptor('foo', default='bar')

    def test_gets_default(self):
        self.failUnlessEqual(self.widget.foo, 'bar')

class TestDisplayChild(WidgetRequireTestCase):
    require = ["Genshi"]
    class TestWidget(Widget):
        class ChildWidget(Widget):
            params = "foo", "bar"
            template = "$foo$bar"
        children = [ChildWidget('child')]
        template = "<span>${display_child('child', **extra_args)}</span>"
        engine_name = 'genshi'
        params = ["extra_args"]
        extra_args = {}

    def test_normal_display(self):
        self.assertInOutput('<span>NoneNone</span>')
    
    def test_display_child_accepts_kw(self):
        self.assertInOutput(
            '<span>foobar</span>', extra_args=dict(foo='foo',bar='bar')
            )

class TestWidgetBunch(TestCase):
    def test_can_setattr(self):
        b = WidgetBunch()
        b.a = Widget('a')
        b.b = Widget('b')
        self.failUnlessEqual(b[0]._id, 'a')
        self.failUnlessEqual(b.a._id, 'a')
        self.failUnlessEqual(b[1]._id, 'b')
        self.failUnlessEqual(b.b._id, 'b')


_ = lazystring

class TestTranslation(WidgetTestCase):
    def setUp(self):
        WidgetTestCase.setUp(self)
        from tw import framework
        self._old = framework.translator
        framework.translator = lambda s: ''.join(reversed(s))

    def tearDown(self):
        WidgetTestCase.tearDown(self)
        from tw import framework
        framework.translator = self._old


    class TestWidget(Widget):
        template = "$value"
        default = _("Foo")

    def test_class_attr_is_translated(self):
        self.assertInOutput("ooF")

    def test_value_at_display_is_translated(self):
        self.assertInOutput("raB", _("Bar"))
