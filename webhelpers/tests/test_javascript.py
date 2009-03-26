from util import WebHelpersTestCase
import unittest

from webhelpers.rails.javascript import *

class TestJavascriptHelper(WebHelpersTestCase):
    def test_escape_javascript(self):
        self.assertEqual("""This \\"thing\\" is really\\n netos\\'""",
               escape_javascript("""This "thing" is really\n netos'"""))
        self.assertEqual("""alert(\\'C:\\\\Program Files\\');""",
               escape_javascript("""alert('C:\Program Files');"""))

    def test_escape_javascript_tag(self):
        self.assertEqual("""<script type="text/javascript">\n//<![CDATA[\nalert(\'All is good\')\n//]]>\n</script>""",
                         javascript_tag("alert('All is good')"))
        self.assertEqual("""<script defer="True" type="text/javascript">\n//<![CDATA[\nalert(\'All is good\')\n//]]>\n</script>""",
                         javascript_tag("alert('All is good')", defer=True))
    
    def test_link_to_funcion(self):
        self.assertEqual("""<a href="#" onclick="alert('Hello World!'); return false;">Greeting</a>""",
               link_to_function("Greeting", "alert('Hello World!')"))
    
    def test_link_to_function_with_html_args(self):
        self.assertEqual("""<a href="/home" onclick="alert('Hello World!'); return false;">Greeting</a>""",
               link_to_function("Greeting", "alert('Hello World!')", href="/home"))

    def test_button_to_function(self):
        input_str = \
            """<input onclick="alert('Hello World!'); " type="button" value="Greeting"></input>"""
        self.assertEqual(input_str,
                         button_to_function("Greeting", "alert('Hello World!')"))

if __name__ == '__main__':
    suite = [unittest.makeSuite(TestJavascriptHelper)]
    for testsuite in suite:
        unittest.TextTestRunner(verbosity=1).run(testsuite)
