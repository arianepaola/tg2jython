import gc
from tw.core.testutil import RequireMixin
from tw.api import Widget
from unittest import TestCase

class TestFuncClosureLeaks(RequireMixin, TestCase):
    """
    In [78]: h.setref()

    In [79]: FormField.engine_name = "mako"

    In [80]: (h.heap()&AddUserForm)
    Out[80]: hpy().Nothing

    In [81]: dummy = AddUserForm("foo").render()

    In [82]: (h.heap()&AddUserForm)
    Out[82]: hpy().Nothing

    In [83]: FormField.engine_name = "genshi"

    In [84]: dummy = AddUserForm("foo").render()

    In [85]: (h.heap()&AddUserForm)
    Out[85]: 
    Partition of a set of 1 object. Total size = 28 bytes.
     Index  Count   %     Size   % Cumulative  % Kind (class / dict of class)
          0      1 100       28 100        28 100 0x8c46584

    In [86]: (h.heap()&AddUserForm).get_rp()
    Out[86]: 
    Reference Pattern by <[dict of] class>.
    0: _ --- [-] 1 0x8c46584: 0x994648c
    1: a      [-] 3 __builtin__.cell: 0x971c02c, 0x971c20c, 0x971ca94
    2: aa ---- [-] 3 tuple: 0x8d8c93c*3, 0x8d958c4*3, 0x970a22c*1
    3: a3       [-] 3 function: toscawidgets.core.display_child...
    4: a4 ------ [-] 1 dict (no owner): 0x992c2d4*36
    5: a5         [-] 1 collections.deque: 0x96aac2c
    6: a6 -------- [-] 1 dict of genshi.template.base.Context: 0x9922e6c
    7: a7           [+] 1 genshi.template.base.Context: 0x9922e6c
    8: a5b ------- [-] 2 types.BuiltinFunctionType: None.appendleft...
    9: a5ba         [^ 6] 1 dict of genshi.template.base.Context: 0x9922e6c

    In [87]: (h.heap()&AddUserForm).sp
    Out[87]: 
    0: hpy().Root.??.tb_frame.f_back.f_back.f_back.f_back.f_back.f_locals['data'].__dict__['frames'].??['display_child'].func_closure[1]->ob_ref
    1: hpy().Root.??.tb_frame.f_back.f_back.f_back.f_back.f_back.f_locals['data'].__dict__['frames'].??['display_field_for'].func_closure[1]->ob_ref
    2: hpy().Root.??.tb_frame.f_back.f_back.f_back.f_back.f_back.f_locals['data'].__dict__['frames'].??['field_for'].func_closure[0]->ob_ref
    3: hpy().Root.??.tb_frame.f_back.f_back.f_back.f_back.f_globals['data'].__dict__['frames'].??['display_child'].func_closure[1]->ob_ref
    4: hpy().Root.??.tb_frame.f_back.f_back.f_back.f_back.f_globals['data'].__dict__['frames'].??['display_field_for'].func_closure[1]->ob_ref
    5: hpy().Root.??.tb_frame.f_back.f_back.f_back.f_back.f_globals['data'].__dict__['frames'].??['field_for'].func_closure[0]->ob_ref
    6: hpy().Root.??.tb_frame.f_back.f_back.f_back.f_back.f_locals['data'].__dict__['frames'].??['display_child'].func_closure[1]->ob_ref
    7: hpy().Root.??.tb_frame.f_back.f_back.f_back.f_back.f_locals['data'].__dict__['frames'].??['display_field_for'].func_closure[1]-
    """
    require = ["tw.forms", "Genshi", "Guppy"]

    def setUp(self):
        super(TestFuncClosureLeaks, self).setUp()
        from guppy import hpy
        self.h = hpy()
        from tw.forms.samples import AddUserForm
        self.widget_cls = AddUserForm
        self.h.setref()


    def test_no_leaks_on_display(self):
        self.widget_cls('form', engine_name='genshi').render()
        gc.collect()
        # fail unless no living AddUserForm instances
        uncollected = self.h.heap()&Widget
        if uncollected:
            self.fail("Leaked widgets!: %s" % uncollected.sp)

    def test_no_leaks_with_args_for(self):
        class TestWidget(Widget):
            template = """\
            <div xmlns:py="http://genshi.edgewall.org/">
            ${args_for(c.fooo)}
            </div>"""
            children = [Widget("fooo")]
            engine_name = "genshi"
        TestWidget().render()
        gc.collect()
        # fail unless no living AddUserForm instances
        uncollected = self.h.heap()&TestWidget
        if uncollected:
            self.fail("Leaked widgets!: %s" % uncollected.sp)

    def test_no_leaks_with_value_for(self):
        class TestWidget(Widget):
            template = """\
            <div xmlns:py="http://genshi.edgewall.org/">
            ${value_for(c.fooo)}
            </div>"""
            children = [Widget("fooo")]
            engine_name = "genshi"
        TestWidget().render()
        gc.collect()
        # fail unless no living AddUserForm instances
        uncollected = self.h.heap()&TestWidget
        if uncollected:
            self.fail("Leaked widgets!: %s" % uncollected.sp)
