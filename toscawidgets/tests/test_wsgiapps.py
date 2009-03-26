import os
import sys
import pkg_resources
from unittest import TestCase

from tw.core.testutil import RequireMixin

examples_dir = os.path.join(pkg_resources.get_distribution('ToscaWidgets').location,
                            'examples')
sys.path.insert(0, examples_dir)

#TODO: Test if resources are served properly

class TestWSGIApp(RequireMixin, TestCase):
    require = ["tw.forms", "Genshi", "WebTest", "BeautifulSoup"]
    def setUp(self):
        super(TestWSGIApp, self).setUp()
        from wsgi_app import app
        from webtest import TestApp
        self.app = TestApp(app)

    def test_resources_included(self):
        response = self.app.get('/')
        self.failUnless('<script' in response)
        self.failUnless('<link' in response)

    def test_full_response_content(self):
        response = self.app.get('/')
        self.failUnless('</body>' in response)

    def test_scripts_are_fetchable(self):
        response = self.app.get('/')
        tags = list(response.html.findAll('script', src=True))
        self.failUnless(tags, "No script tags were found:\n%s" % response)
        for e in tags:
            self.app.get(e['src'])

    def test_links_are_fetchable(self):
        response = self.app.get('/')
        tags = list(response.html.findAll('link', href=True))
        self.failUnless(tags, "No link tags were found:\n%s" % response)
        for e in tags:
            self.app.get(e['href'])
        
