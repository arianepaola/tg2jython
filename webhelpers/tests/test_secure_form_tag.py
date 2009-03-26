# -*- coding: utf-8 -*-
from util import WebHelpersTestCase
import unittest

from webhelpers.rails.secure_form_tag import authentication_token, \
    get_session, secure_form, secure_form_remote_tag, secure_button_to, token_key
from webhelpers.rails.urls import url

class TestSecureFormTagHelper(WebHelpersTestCase):
    def setUp(self):
        super(self.__class__, self).setUp()
        self.authentication_token = authentication_token()
        assert self.authentication_token
        assert get_session()[token_key] == self.authentication_token
        
    def test_secure_form(self):
        self.assertEqual(
            secure_form(url="http://www.example.com"),
            '<form action="http://www.example.com" method="POST">\n<div style="display: none;"><input id="%s" name="%s" type="hidden" value="%s" /></div>' % (token_key, token_key, self.authentication_token)
        )
        self.assertEqual(
            secure_form(url="http://www.example.com", method='GET'),
            '<form action="http://www.example.com" method="GET">\n<div style="display: none;"><input id="%s" name="%s" type="hidden" value="%s" /></div>' % (token_key, token_key, self.authentication_token)
        )
        self.assertEqual(
            secure_form(url('/test/edit/1')),
            '<form action="/test/edit/1" method="POST">\n<div style="display: none;"><input id="%s" name="%s" type="hidden" value="%s" /></div>' % (token_key, token_key, self.authentication_token)
        )

    def test_secure_form_remote_tag(self):
        self.assertEqual(secure_form_remote_tag(update="glass_of_beer",url='http://www.example.com/fast'),
        """<form action="http://www.example.com/fast" method="POST" onsubmit="new Ajax.Updater(\'glass_of_beer\', \'http://www.example.com/fast\', {asynchronous:true, evalScripts:true, parameters:Form.serialize(this)}); return false;">\n<div style="display: none;"><input id="%s" name="%s" type="hidden" value="%s" /></div>""" % (token_key, token_key, self.authentication_token))
        
    def test_secure_button_to(self):
        self.assertEqual(
            secure_button_to(name="Example", url="http://www.example.com"), 
            """<form method=\"POST\" action=\"http://www.example.com\" class=\"button-to\"><div><input type=\"submit\" value=\"Example\" /></div>\n<div style="display:none;"><input id="%s" name="%s" type="hidden" value="%s" /></div></form>""" % (token_key, token_key, self.authentication_token)
        )

if __name__ == '__main__':
    suite = [unittest.makeSuite(TestSecureFormTagHelper)]
    for testsuite in suite:
        unittest.TextTestRunner(verbosity=1).run(testsuite)
