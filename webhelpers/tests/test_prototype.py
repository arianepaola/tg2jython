from util import WebHelpersTestCase
import unittest

from webhelpers.rails.urls import *
from webhelpers.rails.prototype import *
from routes import *

class TestPrototypeHelper(WebHelpersTestCase):
    def test_link_to_remote(self):
        self.assertEqual("""<a class="fine" href="#" onclick="new Ajax.Request('http://www.example.com/whatnot', {asynchronous:true, evalScripts:true}); return false;">Remote outpost</a>""",
            link_to_remote("Remote outpost", dict(url='http://www.example.com/whatnot'), class_="fine"))
        self.assertEqual("""<a href="#" onclick="new Ajax.Request('http://www.example.com/whatnot', {asynchronous:true, evalScripts:true, onComplete:function(request){alert(request.reponseText)}}); return false;">Remote outpost</a>""",
            link_to_remote("Remote outpost", dict(complete="alert(request.reponseText)",url='http://www.example.com/whatnot')))
        self.assertEqual("""<a href="#" onclick="new Ajax.Request('http://www.example.com/whatnot', {asynchronous:true, evalScripts:true, onSuccess:function(request){alert(request.reponseText)}}); return false;">Remote outpost</a>""",
            link_to_remote("Remote outpost", dict(success="alert(request.reponseText)",url='http://www.example.com/whatnot')))
        self.assertEqual("""<a href="#" onclick="new Ajax.Request('http://www.example.com/whatnot', {asynchronous:true, evalScripts:true, onFailure:function(request){alert(request.reponseText)}}); return false;">Remote outpost</a>""",
            link_to_remote("Remote outpost", dict(failure="alert(request.reponseText)",url='http://www.example.com/whatnot')))
        self.assertEqual("<a href=\"#\" onclick=\"new Ajax.Request('http://www.example.com/whatnot?a=10&amp;b=20', {asynchronous:true, evalScripts:true, onFailure:function(request){alert(request.reponseText)}}); return false;\">Remote outpost</a>",
            link_to_remote("Remote outpost", dict(failure="alert(request.reponseText)",url ='http://www.example.com/whatnot?a=10&b=20')))

    def test_periodically_call_remote(self):
        self.assertEqual("""<script type="text/javascript">\n//<![CDATA[\nnew PeriodicalExecuter(function() {new Ajax.Updater('schremser_bier', 'http://www.example.com/mehr_bier', {asynchronous:true, evalScripts:true})}, 10)\n//]]>\n</script>""",
            periodically_call_remote(update="schremser_bier",url='http://www.example.com/mehr_bier'))

    def test_form_remote_tag(self):
        self.assertEqual("""<form action="http://www.example.com/fast" method="POST" onsubmit="new Ajax.Updater('glass_of_beer', 'http://www.example.com/fast', {asynchronous:true, evalScripts:true, parameters:Form.serialize(this)}); return false;">""",
            form_remote_tag(update="glass_of_beer",url='http://www.example.com/fast'))
        self.assertEqual("""<form action="http://www.example.com/fast" method="POST" onsubmit="new Ajax.Updater({success:'glass_of_beer'}, 'http://www.example.com/fast', {asynchronous:true, evalScripts:true, parameters:Form.serialize(this)}); return false;">""",
            form_remote_tag(update=dict(success="glass_of_beer"), url='http://www.example.com/fast'))
        self.assertEqual("""<form action="http://www.example.com/fast" method="POST" onsubmit="new Ajax.Updater({failure:'glass_of_water'}, 'http://www.example.com/fast', {asynchronous:true, evalScripts:true, parameters:Form.serialize(this)}); return false;">""",
            form_remote_tag(update=dict(failure="glass_of_water"),url='http://www.example.com/fast'))
        self.assertEqual("""<form action="http://www.example.com/fast" method="POST" onsubmit="new Ajax.Updater({success:'glass_of_beer',failure:'glass_of_water'}, 'http://www.example.com/fast', {asynchronous:true, evalScripts:true, parameters:Form.serialize(this)}); return false;">""",
            form_remote_tag(update=dict(success='glass_of_beer',failure="glass_of_water"),url='http://www.example.com/fast'))
            
    def test_form_remote_tag_with_method(self):
        self.assertEqual("""<form action=\"http://www.example.com/fast\" method=\"POST\" onsubmit=\"new Ajax.Updater('glass_of_beer', 'http://www.example.com/fast', {asynchronous:true, evalScripts:true, parameters:Form.serialize(this)}); return false;\"><input id="_method" name="_method" type="hidden" value="PUT" />""",
            form_remote_tag(update="glass_of_beer", url='http://www.example.com/fast', html={'method':'PUT'}))
        self.assertEqual("""<form action=\"http://www.example.com/fast\" method=\"POST\" onsubmit=\"new Ajax.Updater('glass_of_beer', 'http://www.example.com/fast', {asynchronous:true, evalScripts:true, parameters:Form.serialize(this)}); return false;\"><input id="_method" name="_method" type="hidden" value="put" />""",
            form_remote_tag(update="glass_of_beer", url='http://www.example.com/fast', html={'method':'put'}))

    def test_form_remote_tag_with_name(self):
        self.assertEqual("""<form action="http://www.example.com/fast" method="POST" name="testForm" onsubmit="new Ajax.Updater('glass_of_beer', 'http://www.example.com/fast', {asynchronous:true, evalScripts:true, parameters:Form.serialize(this)}); return false;">""",
            form_remote_tag(update="glass_of_beer",url='http://www.example.com/fast', html={'name':"testForm"}))
        
    def test_on_callbacks(self):
        callbacks = ['uninitialized','loading','loaded','interactive','complete','success','failure']
        for callback in callbacks:
            self.assertEqual("""<form action="http://www.example.com/fast" method="POST" onsubmit="new Ajax.Updater('glass_of_beer', 'http://www.example.com/fast', {asynchronous:true, evalScripts:true, on%s:function(request){monkeys();}, parameters:Form.serialize(this)}); return false;">""" % callback.title(),
                form_remote_tag(update="glass_of_beer", url='http://www.example.com/fast',**{callback:"monkeys();"}))
            self.assertEqual("""<form action="http://www.example.com/fast" method="POST" onsubmit="new Ajax.Updater({success:'glass_of_beer'}, 'http://www.example.com/fast', {asynchronous:true, evalScripts:true, on%s:function(request){monkeys();}, parameters:Form.serialize(this)}); return false;">""" % callback.title(),
                form_remote_tag(update={'success':"glass_of_beer"},url='http://www.example.com/fast',**{callback:"monkeys();"}))
            self.assertEqual("""<form action="http://www.example.com/fast" method="POST" onsubmit="new Ajax.Updater({failure:'glass_of_beer'}, 'http://www.example.com/fast', {asynchronous:true, evalScripts:true, on%s:function(request){monkeys();}, parameters:Form.serialize(this)}); return false;">""" % callback.title(),
                form_remote_tag(update={'failure':"glass_of_beer"},url='http://www.example.com/fast',**{callback:"monkeys();"}))
            self.assertEqual("""<form action="http://www.example.com/fast" method="POST" onsubmit="new Ajax.Updater({success:'glass_of_beer',failure:'glass_of_water'}, 'http://www.example.com/fast', {asynchronous:true, evalScripts:true, on%s:function(request){monkeys();}, parameters:Form.serialize(this)}); return false;">""" % callback.title(),
                form_remote_tag(update={'success':"glass_of_beer",'failure':"glass_of_water"},url='http://www.example.com/fast',**{callback:"monkeys();"}))

        #HTTP status codes 100 up to 599 have callbacks
        #these should work
        for callback in [str(x) for x in range(100,599)]:
            self.assertEqual("""<form action="http://www.example.com/fast" method="POST" onsubmit="new Ajax.Updater('glass_of_beer', 'http://www.example.com/fast', {asynchronous:true, evalScripts:true, on%s:function(request){monkeys();}, parameters:Form.serialize(this)}); return false;">""" % callback,
                form_remote_tag(update="glass_of_beer",url='http://www.example.com/fast', **{callback:"monkeys();"}))

        #test 200 and 404
        self.assertEqual("""<form action="http://www.example.com/fast" method="POST" onsubmit="new Ajax.Updater('glass_of_beer', 'http://www.example.com/fast', {asynchronous:true, evalScripts:true, on200:function(request){monkeys();}, on404:function(request){bananas();}, parameters:Form.serialize(this)}); return false;">""",
            form_remote_tag(update="glass_of_beer",url='http://www.example.com/fast',**{'200':"monkeys();",'404':"bananas();"}))

        #these shouldn't
        for callback in [str(x) for x in range(1,99)]:
            self.assertEqual("""<form action="http://www.example.com/fast" method="POST" onsubmit="new Ajax.Updater('glass_of_beer', 'http://www.example.com/fast', {asynchronous:true, evalScripts:true, parameters:Form.serialize(this)}); return false;">""",
                form_remote_tag(update="glass_of_beer",url='http://www.example.com/fast',**{callback:"monkeys();"}))
        for callback in [str(x) for x in range(600,999)]:
            self.assertEqual("""<form action="http://www.example.com/fast" method="POST" onsubmit="new Ajax.Updater('glass_of_beer', 'http://www.example.com/fast', {asynchronous:true, evalScripts:true, parameters:Form.serialize(this)}); return false;">""",
                form_remote_tag(update="glass_of_beer",url='http://www.example.com/fast',**{callback:"monkeys();"}))

        #test ultimate combo
        self.assertEqual("""<form action="http://www.example.com/fast" method="POST" onsubmit="new Ajax.Updater('glass_of_beer', 'http://www.example.com/fast', {asynchronous:true, evalScripts:true, on200:function(request){monkeys();}, on404:function(request){bananas();}, onComplete:function(request){c();}, onFailure:function(request){f();}, onLoading:function(request){c1()}, onSuccess:function(request){s()}, parameters:Form.serialize(this)}); return false;">""",
            form_remote_tag(update="glass_of_beer",url='http://www.example.com/fast',loading="c1()",success="s()",failure="f();",complete="c();",**{'200':"monkeys();",'404':"bananas();"}))

    def test_submit_to_remote(self):
        self.assertEqual("""<input name="More beer!" onclick="new Ajax.Updater('empty_bottle', 'http://www.example.com/', {asynchronous:true, evalScripts:true, parameters:Form.serialize(this.form)}); return false;" type="button" value="1000000" />""",
            submit_to_remote("More beer!", 1000000,update="empty_bottle",url='http://www.example.com/'))

    def test_observe_field(self):
        self.assertEqual("""<script type="text/javascript">\n//<![CDATA[\nnew Form.Element.Observer('glass', 300, function(element, value) {new Ajax.Request('http://www.example.com/reorder_if_empty', {asynchronous:true, evalScripts:true})})\n//]]>\n</script>""",
            observe_field("glass", frequency=300,url='http://www.example.com/reorder_if_empty'))
        self.assertEqual("""<script type="text/javascript">\n//<![CDATA[\nnew Form.Element.Observer('glass', 300, function(element, value) {new Ajax.Request('http://www.example.com/reorder_if_empty', {asynchronous:true, evalScripts:true})}, 'blur')\n//]]>\n</script>""",
            observe_field("glass", frequency=300,url='http://www.example.com/reorder_if_empty',on="blur"))

    def test_observe_form(self):
        self.assertEqual("""<script type="text/javascript">\n//<![CDATA[\nnew Form.Observer('cart', 2, function(element, value) {new Ajax.Request('http://www.example.com/cart_changed', {asynchronous:true, evalScripts:true, parameters:Form.serialize('cart')})})\n//]]>\n</script>""",
            observe_form("cart", frequency=2,url='http://www.example.com/cart_changed'))

    def test_update_element_function(self):
        self.assertEqual("""$('myelement').innerHTML = 'blub';\n""",
            update_element_function('myelement',content='blub'))
        self.assertEqual("""$('myelement').innerHTML = 'blub';\n""",
            update_element_function('myelement',action='update',content='blub'))
        self.assertEqual("""$('myelement').innerHTML = '';\n""",
            update_element_function('myelement',action='empty'))
        self.assertEqual("""Element.remove('myelement');\n""",
            update_element_function('myelement',action='remove'))

        self.assertEqual("""new Insertion.Bottom('myelement','blub');\n""",
            update_element_function('myelement',position='bottom',content='blub'))
        self.assertEqual("""new Insertion.Bottom('myelement','blub');\n""",
            update_element_function('myelement',action='update',position='bottom',content='blub'))
    

if __name__ == '__main__':
    suite = [unittest.makeSuite(TestPrototypeHelper)]
    for testsuite in suite:
        unittest.TextTestRunner(verbosity=1).run(testsuite)
