from dbsprockets.viewfactory import ViewFactory
from dbsprockets.viewconfig import ViewConfig
from dbsprockets.metadata import Metadata, NotFoundError
from dbsprockets.iprovider import IProvider

class DummyMetadata(Metadata):
    def _doKeys(self):
        return []
    

class DummyViewConfig(ViewConfig):
    metadataType = DummyMetadata
    
class testViewFactory:
    def setup(self):
        provider = IProvider()
        self.viewFactory = ViewFactory()
        self.viewConfig = DummyViewConfig(provider, 'test_table')
        
    def testCreateObj(self):
        pass
    
    def testCreate(self):
        view  = self.viewFactory.create(self.viewConfig)
    