from nose.tools import raises
from tw.api import Widget

from dbsprockets.iprovider import IProvider
from dbsprockets.sprockets import Views, Sessions, Sprocket, Sprockets, SessionConfigError, ViewConfigError
from dbsprockets.view import View
from dbsprockets.sessionconfig import SessionConfig
from dbsprockets.viewconfig import ViewConfig
from dbsprockets.metadata import Metadata

class TestSprockets:
    pass

class TestViews:
    provider = IProvider()
    def setup(self):
        self.views = Views(self.provider, '')
        
    def testCreate(self):
        pass
    
    @raises(TypeError)
    def _create(self, provider, controller=''):
        Views(provider, controller)
        
    def testCreateBad(self):
        provider = IProvider()
        badInput = ('a', (), {}, [], 1, 1.2)
        for input in badInput:
            yield self._create, badInput
        for input in badInput[1:]:
            yield self._create, provider, badInput
            
    @raises(TypeError)
    def testPutBad(self):
        self.views['lala'] = 'lala'
    
    def testPut(self):
        viewConfig = ViewConfig(self.provider,'')
        view = View(Widget, viewConfig)
        self.views['test'] = view
        
    @raises(ViewConfigError)
    def testGetBadViewConfigType(self):
        self.views['testBad__tableName']

    def testGet(self):
        viewConfig = ViewConfig(self.provider,'')
        view = View(Widget, viewConfig)
        self.views['test'] = view
        assert self.views['test'] == view
        
    @raises(TypeError)
    def testGetBad(self):
        self.views[1]
        
class TestSessions:
    provider = IProvider()
    def setup(self):
        self.sessions = Sessions(self.provider)
        
    def testCreate(self):
        pass
    
    @raises(TypeError)
    def _create(self, arg1):
        Sessions(arg1)
        
    def testCreateBad(self):
        badInput = ((), {}, [], 'a', 1, 1.2)
        for input in badInput:
            yield self._create, badInput
            
    @raises(TypeError)
    def testPutBad(self):
        self.sessions['lala'] = 'lala'
    
    def testPut(self):
        sessionConfig = SessionConfig('', self.provider)
        self.sessions['test'] = sessionConfig
    
    def testGet(self):
        sessionConfig = SessionConfig('', self.provider)
        self.sessions['test'] = sessionConfig
        assert self.sessions['test'] is sessionConfig
    
    @raises(SessionConfigError)
    def testGetBadSessionConfigType(self):
        self.sessions['testBad__tableName']
        
    @raises(TypeError)
    def testGetBad(self):
        self.sessions[1]
        
class TestSprocket:
    provider = IProvider()
    sessionConfig = SessionConfig('',provider)
    viewConfig = ViewConfig(provider, '')
    view = View(Widget, viewConfig)
    
    def setup(self):
        self.sprocket = Sprocket(self.view, self.sessionConfig)
        
    def testCreate(self):
        pass
    
    @raises(TypeError)
    def _create(self, arg1, arg2=None):
        Sprocket(arg1, arg2)
        
    def testCreateBad(self):
        badInput = ((), {}, [], 'a', 1, 1.2)
        for input in badInput:
            yield self._create, input

        badInput = ((), {}, [], 'a', 1, 1.2)
        for input in badInput:
            yield self._create, self.view, input

class TestSprockets:
    provider = IProvider()
    def setup(self):
        self.sprockets = Sprockets(self.provider, '')
        
    def testCreate(self):
        pass
    
    @raises(TypeError)
    def _create(self, arg1, arg2=''):
        Sprockets(arg1, arg2)
        
    def testCreateBad(self):
        provider = IProvider()
        badInput = ('a', (), {}, [], 1, 1.2)
        for input in badInput:
            yield self._create, badInput
        for input in badInput[1:]:
            yield self._create, provider, badInput
            
    @raises(TypeError)
    def testPutBad(self):
        self.sprockets['lala'] = 'lala'
    
    def testPut(self):
        sessionConfig = SessionConfig('', self.provider)
        viewConfig = ViewConfig(self.provider, '')
        view = View(Widget, viewConfig)
        sprocket = Sprocket(view, sessionConfig)
        self.sprockets['test'] = sprocket
        
    def testGet(self):
        sessionConfig = SessionConfig('',self.provider)
        viewConfig = ViewConfig(self.provider, '')
        view = View(Widget, viewConfig)
        sprocket = Sprocket(view, sessionConfig)
        self.sprockets['test'] = sprocket
        gotSprocket = self.sprockets['test']
        assert gotSprocket == sprocket
        
    @raises(TypeError)
    def testGetBad(self):
        self.sprockets[1]