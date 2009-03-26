from dbsprockets.view import View
from tw.api import Widget
from dbsprockets.viewconfig import ViewConfig
from dbsprockets.metadata import Metadata
from dbsprockets.iprovider import IProvider

class testView:
    def setup(self):
        provider = IProvider()
#        metadata = Metadata(provider)
        viewConfig = ViewConfig(provider, '')
        
        self.view = View(Widget(), viewConfig)
        
    def testCreate(self):
        pass
    
    def testDisplay(self):
        s = self.view.widget(value={})
        assert s == None, s