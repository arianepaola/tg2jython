from projectname.tests import *

class TestSample2Controller(TestController):
    def test_get(self):
        response = self.app.get(url_for(controller='/sample', action='test_only_get'))
        assert 'It was a get' in response
    
    def test_redir_get(self):
        response = self.app.get(url_for(controller='/sample', action='test_only_post'))
        assert 'It was a get' in response
        
    def test_post(self):
        response = self.app.post(url_for(controller='/sample', action='test_only_post'),
            params={'id':4})
        assert 'It was a post' in response
