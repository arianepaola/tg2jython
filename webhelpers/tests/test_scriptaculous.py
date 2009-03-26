from util import WebHelpersTestCase
import unittest

from webhelpers.rails.scriptaculous import *

class TestScriptaculousHelper(WebHelpersTestCase):
    def test_effect(self):
        self.assertEqual("new Effect.Highlight('posts',{});", visual_effect('highlight', "posts"))
        self.assertEqual("new Effect.Fade('fademe',{duration:4.0});", visual_effect('fade', "fademe", duration=4.0))
        self.assertEqual("new Effect.Shake(element,{});", visual_effect('shake'))
        self.assertEqual("new Effect.DropOut('dropme',{queue:'end'});", visual_effect('drop_out', 'dropme',queue='end'))

        def compare(expected, result, begin, end, *tokens):
            """Compare expected to result without assuming CPython dict ordering"""
            self.assertEqual(len(expected), len(result))
            self.assert_(result.startswith(expected[:expected.find(begin) + 1]))
            self.assert_(result.endswith(end), result)
            for token in tokens:
                self.assert_(token in result)

        compare("new Effect.DropOut('dropme',{queue:{scope:'test',limit:2,position:'end'}});",
                visual_effect('drop_out', 'dropme', queue=dict(position="end",scope="test", limit=2)),
                '{queue', "}});", "scope:'test'", "limit:2", "position:'end'")
        compare("new Effect.DropOut('dropme',{queue:{scope:'list',limit:2}});",
                visual_effect('drop_out', 'dropme', queue=dict(scope='list',limit=2)),
                '{queue', "}});", "scope:'list'", "limit:2")
        compare("new Effect.DropOut('dropme',{queue:{scope:'test',limit:2,position:'end'}});",
                visual_effect('drop_out', 'dropme', queue=dict(position='end',scope='test',limit=2)),
                '{queue', "}});", "scope:'test'", "limit:2", "position:'end'")
    
    def test_toggle_effects(self):
        self.assertEqual("Effect.toggle('posts','appear',{});", visual_effect("toggle_appear", "posts"))
        self.assertEqual("Effect.toggle('posts','slide',{});", visual_effect("toggle_slide", "posts"))
        self.assertEqual("Effect.toggle('posts','blind',{});", visual_effect("toggle_blind", "posts"))
    
    def test_sortable_element(self):
        self.assertEqual("""<script type="text/javascript">\n//<![CDATA[\nSortable.create('mylist', {onUpdate:function(){new Ajax.Request('http://www.example.com/order', {asynchronous:true, evalScripts:true, parameters:Sortable.serialize('mylist')})}})\n//]]>\n</script>""", 
            sortable_element("mylist",url='http://www.example.com/order'))
        self.assertEqual("""<script type="text/javascript">\n//<![CDATA[\nSortable.create('mylist', {constraint:'horizontal', onUpdate:function(){new Ajax.Request('http://www.example.com/order', {asynchronous:true, evalScripts:true, parameters:Sortable.serialize('mylist')})}, tag:'div'})\n//]]>\n</script>""",
            sortable_element("mylist",tag="div",constraint="horizontal",url='http://www.example.com/order'))
        self.assertEqual("""<script type="text/javascript">\n//<![CDATA[\nSortable.create('mylist', {constraint:'horizontal', containment:['list1','list2'], onUpdate:function(){new Ajax.Request('http://www.example.com/order', {asynchronous:true, evalScripts:true, parameters:Sortable.serialize('mylist')})}})\n//]]>\n</script>""",
            sortable_element("mylist",containment=['list1','list2'], constraint="horizontal",url='http://www.example.com/order'))
        self.assertEqual("""<script type="text/javascript">\n//<![CDATA[\nSortable.create('mylist', {constraint:'horizontal', containment:'list1', onUpdate:function(){new Ajax.Request('http://www.example.com/order', {asynchronous:true, evalScripts:true, parameters:Sortable.serialize('mylist')})}})\n//]]>\n</script>""", 
            sortable_element("mylist",containment='list1',constraint="horizontal",url='http://www.example.com/order'))

    def test_draggable_element(self):
        self.assertEqual("""<script type="text/javascript">\n//<![CDATA[\nnew Draggable('product_13', {})\n//]]>\n</script>""",
            draggable_element('product_13'))
        self.assertEqual("""<script type="text/javascript">\n//<![CDATA[\nnew Draggable('product_13', {revert:true})\n//]]>\n</script>""",
            draggable_element('product_13',revert=True))

    def test_drop_receiving_element(self):
        self.assertEqual("""<script type="text/javascript">\n//<![CDATA[\nDroppables.add('droptarget1', {onDrop:function(element){new Ajax.Request('http://www.example.com/', {asynchronous:true, evalScripts:true, parameters:'id=' + encodeURIComponent(element.id)})}})\n//]]>\n</script>""",
            drop_receiving_element('droptarget1',url='http://www.example.com/'))
        self.assertEqual("""<script type="text/javascript">\n//<![CDATA[\nDroppables.add('droptarget1', {accept:'products', onDrop:function(element){new Ajax.Request('http://www.example.com/', {asynchronous:true, evalScripts:true, parameters:'id=' + encodeURIComponent(element.id)})}})\n//]]>\n</script>""",
            drop_receiving_element('droptarget1',url='http://www.example.com/',accept='products'))
        self.assertEqual("""<script type="text/javascript">\n//<![CDATA[\nDroppables.add('droptarget1', {accept:'products', onDrop:function(element){new Ajax.Updater('infobox', 'http://www.example.com/', {asynchronous:true, evalScripts:true, parameters:'id=' + encodeURIComponent(element.id)})}})\n//]]>\n</script>""",
            drop_receiving_element('droptarget1',accept='products',update='infobox',url='http://www.example.com/'))
        self.assertEqual("""<script type="text/javascript">\n//<![CDATA[\nDroppables.add('droptarget1', {accept:['tshirts','mugs'], onDrop:function(element){new Ajax.Updater('infobox', 'http://www.example.com/', {asynchronous:true, evalScripts:true, parameters:'id=' + encodeURIComponent(element.id)})}})\n//]]>\n</script>""",
            drop_receiving_element('droptarget1',accept=['tshirts','mugs'],update='infobox',url='http://www.example.com/'))


if __name__ == '__main__':
    suite = [unittest.makeSuite(TestScriptaculousHelper)]
    for testsuite in suite:
        unittest.TextTestRunner(verbosity=1).run(testsuite)
