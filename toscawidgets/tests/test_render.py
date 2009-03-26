# -*- coding: utf-8 -*-
from tw import framework
from tw.api import Widget, Renderable
from unittest import TestCase
from tw.core.testutil import RequireMixin, WidgetMixin, WidgetTestCase

def set_view(view):
    framework.default_view = view



class TestBasic(WidgetMixin, TestCase):
    class TestWidget(Widget):
        pass

    def test_no_template_returns_None(self):
        self.failUnlessEqual(self.widget.display(), None)
        self.failUnlessEqual(self.widget.render(), None)

class RenderMixin(RequireMixin):
    require = ["Genshi", "Kid >= 0.9.5", "TurboKid >= 0.9.9", "TurboCheetah", 
               "Mako"]

    def test_display(self):
        self.assert_(isinstance(self.widget.display(), basestring))

    def test_display_on_genshi(self):
        set_view('genshi')
        output = self.widget.display()
        self.assert_(hasattr(output, '__iter__'))

    def test_display_on_genshi_override_at_display(self):
        output = self.widget.display(displays_on="genshi")
        self.assert_(hasattr(output, '__iter__'))

    def test_display_on_kid(self):
        set_view('kid')
        output = self.widget.display()
        #XXX: Better way to check this needed, where is Element defined??
        self.assert_('Element' in repr(output), repr(output))
    
    def test_display_on_kid_override_at_display(self):
        output = self.widget.display(displays_on="kid")
        #XXX: Better way to check this needed, where is Element defined??
        self.assert_('Element' in repr(output), repr(output))

    def test_display_on_cheetah(self):
        set_view('cheetah')
        self.assert_(isinstance(self.widget.display(), basestring))

    def test_display_on_cheetah_override_at_display(self):
        self.assert_(
            isinstance(self.widget.display(displays_on="cheetah"), basestring)
            )

    def test_display_on_mako(self):
        set_view('mako')
        self.assert_(isinstance(self.widget.display(), basestring))

    def test_display_on_mako_override_at_display(self):
        self.assert_(
            isinstance(self.widget.display(displays_on="mako"), basestring)
            )

    def test_render_always_produces_unicode(self):
        for dest in "kid mako cheetah genshi".split():
            output = self.widget.render(displays_on=dest)
            self.assert_(isinstance(output, unicode), type(output))
        
class TestRenderable(WidgetTestCase):
    class MyRenderable(Renderable):
        template = "$some_var"

    def setUp(self):
        super(TestRenderable, self).setUp()
        self.widget = self.MyRenderable()
    
    def test_variable_goes_to_template(self):
        self.assertInOutput("Foo", some_var="Foo")


class TestGenshi(RenderMixin, WidgetTestCase):
    class TestWidget(Widget):
        template = """<input 
            xmlns="http://www.w3.org/1999/xhtml"
            xmlns:py="http://genshi.edgewall.org/"
            type="text" value="${value}" id="${id}" />"""
        engine_name = "genshi"

    def test_render(self):
        self.assertInOutput('<input')

    def test_render_value(self):
        self.assertInOutput('foo', 'foo')

    

class TestKid(RenderMixin, WidgetTestCase):
    class TestWidget(Widget):
        template = """<input 
            xmlns:py="http://purl.org/kid/ns#"
            type="text" value="${value}" id="${id}" />"""
        engine_name = "kid"

    def test_render(self):
        self.assertInOutputIC('<INPUT')

    def test_render_value(self):
        self.assertInOutput('foo', 'foo')


    
class TestKidInGenshi(RenderMixin, WidgetTestCase):
    class TestWidget(Widget):
        class KidWidget(Widget):
            template = """<input 
                xmlns:py="http://purl.org/kid/ns#"
                type="text" value="${value}" id="${id}" />"""
            engine_name = "kid"
        children = [KidWidget('kid')]
        template = """
        <div xmlns="http://www.w3.org/1999/xhtml"
             xmlns:py="http://genshi.edgewall.org/"
             id="${id}">${children.kid.display(value_for('kid'))}</div>
        """
        engine_name = "genshi"

    def test_render(self):
        self.assertInOutput(['<input', '<div'])

    def test_render_value(self):
        self.assertInOutput('foo', dict(kid='foo'))


class TestGenshiInKid(RenderMixin, WidgetTestCase):
    class TestWidget(Widget):
        class GenshiWidget(Widget):
            template = """<input 
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:py="http://genshi.edgewall.org/"
                type="text" value="${value}" id="${id}" />"""
            engine_name = "genshi"
        children = [GenshiWidget('genshi')]
        template = """
        <div xmlns:py="http://purl.org/kid/ns#"
             id="${id}">${children.genshi.display(value_for('genshi'))}</div>
        """
        engine_name = "kid"

    def test_render(self):
        self.assertInOutputIC(['<INPUT', '<DIV'])

    def test_render_value(self):
        self.assertInOutput('foo', dict(genshi='foo'))


class TestCheetah(RenderMixin, WidgetTestCase):

    class TestWidget(Widget):
        template = "cheetah:tests.templates.test_cheetah"

    def test_render(self):
        self.assertInOutput('<input')

    def test_render_value(self):
        self.assertInOutput('foo', 'foo')


class TestCheetahInGenshi(RenderMixin, WidgetTestCase):
    class TestWidget(Widget):
        class CheetahWidget(Widget):
            template = "cheetah:tests.templates.test_cheetah"
        children = [CheetahWidget('cheetah')]
        template = """
        <div xmlns="http://www.w3.org/1999/xhtml"
             xmlns:py="http://genshi.edgewall.org/"
             id="${id}">${children.cheetah.display(value_for('cheetah'))}</div>
        """
        engine_name = "genshi"

    def test_render(self):
        self.assertInOutput(['<input', '<div'])

    def test_render_value(self):
        self.assertInOutput('foo', dict(cheetah='foo'))


class TestCheetahInKid(RenderMixin, WidgetTestCase):
    class TestWidget(Widget):
        class CheetahWidget(Widget):
            template = "cheetah:tests.templates.test_cheetah"
        children = [CheetahWidget('cheetah')]
        template = """
        <div xmlns:py="http://purl.org/kid/ns#"
             id="${id}">${children.cheetah.display(value_for('cheetah'))}</div>
        """
        engine_name = "kid"

    def test_render(self):
        self.assertInOutputIC(['<INPUT', '<DIV'])

    def test_render_value(self):
        self.assertInOutput('foo', dict(cheetah='foo'))


class TestStringInKid(RenderMixin, WidgetTestCase):
    class TestWidget(Widget):
        class StringWidget(Widget):
            template = """<input value="$value" />"""
        children = [StringWidget('string')]
        template = """
        <div xmlns:py="http://purl.org/kid/ns#"
             id="${id}">${children.string.display(value_for('string'))}</div>
        """
        engine_name = "kid"

    def test_render(self):
        self.assertInOutputIC(['<INPUT', '<DIV'])

    def test_render_value(self):
        self.assertInOutput('foo', dict(string='foo'))


class TestStringInGenshi(RenderMixin, WidgetTestCase):
    class TestWidget(Widget):
        class StringWidget(Widget):
            template = """<input value="$value" />"""
        children = [StringWidget('string')]
        template = """
        <div xmlns="http://www.w3.org/1999/xhtml"
             xmlns:py="http://genshi.edgewall.org/"
             id="${id}">${children.string.display(value_for('string'))}</div>
        """
        engine_name = "genshi"

    def test_render(self):
        self.assertInOutput(['<input', '<div'])

    def test_render_value(self):
        self.assertInOutput('foo', dict(string='foo'))


class TestMakoInGenshi(RenderMixin, WidgetTestCase):
    class TestWidget(Widget):
        class MakoWidget(Widget):
            params = ["rows"]
            rows = []
            engine_name = "mako"
            template = """
            <%page args="id=''" />
            <table id="${id}">
                % for row in rows:
                    ${makerow(row)}
                % endfor
            </table>
               
            <%def name="makerow(row)">
                <tr>
                % for name in row:
                    <td>${name}</td>
                % endfor
                </tr>
            </%def>
            """
            def update_params(self,d):
                Widget.update_params(self,d)
                if d['value']:
                    rows = d['rows'] = d['value']
                    
        engine_name = "genshi"
        children = [MakoWidget('mako')]
        template = """<div
        xmlns="http://www.w3.org/1999/xhtml"
        xmlns:py="http://genshi.edgewall.org/">${display_child('mako')}</div>"""

    def test_render(self):
        self.assertInOutput(['<table', 'id="test_mako"'])

    def test_render_value(self):
        self.assertInOutput(['<td>foo</td>', '<td>bar</td>'],
                            {'mako':[('foo','bar')]*5})

    def test_render_unicode(self):
        u_str = unicode("Hello w\xc3\xb8rld", 'utf-8')
        value = {'mako':[(u_str,'foo')]}
        output = self.widget.render(value)
        assert u_str in output

class TestMakoInGenshiExternalTemplate(RenderMixin, WidgetTestCase):
    class TestWidget(Widget):
        class MakoWidget(Widget):
            params = ["rows"]
            rows = []
            engine_name = "mako"
            template = "mako:tests.templates.mako_template"
            def update_params(self,d):
                Widget.update_params(self,d)
                if d['value']:
                    rows = d['rows'] = d['value']
                    
        engine_name = "genshi"
        children = [MakoWidget('mako')]
        template = """<div
        xmlns="http://www.w3.org/1999/xhtml"
        xmlns:py="http://genshi.edgewall.org/">${display_child('mako')}</div>"""

    def test_render(self):
        self.assertInOutput(['<table', 'id="test_mako"'])

    def test_render_value(self):
        self.assertInOutput(['<td>foo</td>', '<td>bar</td>'],
                            {'mako':[('foo','bar')]*5})

    def test_render_unicode(self):
        u_str = unicode("Hello w\xc3\xb8rld", 'utf-8')
        value = {'mako':[(u_str,'foo')]}
        output = self.widget.render(value)
        assert u_str in output
