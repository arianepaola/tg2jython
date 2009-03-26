from dbsprockets.test.base import setupDatabase, setupReflection, teardownDatabase
from dbsprockets.test.testSAProvider import _TestSAProvider

def setup():
    setupDatabase()
    setupReflection()
def teardown():
    teardownDatabase()
    
class TestSAProviderReflected(_TestSAProvider):
    pass
