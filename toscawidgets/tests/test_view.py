from tw.api import EngineManager
from unittest import TestCase

class TestEngineManager(TestCase):
    def setUp(self):
        self.em = EngineManager()

    def test_load_all(self):
        self.em.load_all(raise_error=False)
        self.failUnless('toscawidgets' in self.em)

    def test_load_engine(self):
        self.em.load_engine('toscawidgets')
        
    def test_load_from_distribution(self):
        self.em.load_engine('toscawidgets', distribution="ToscaWidgets")


class CustomDeprecatedEngineManager(EngineManager):
    def _initialize_engine(self, name, factory, engine_options=None, stdvars=None):
        if engine_options is None:
            engine_options = {}
        if stdvars is None:
            stdvars = {}
        try:
            def extra_vars():
                return stdvars
            self[name] = factory(extra_vars, engine_options)
            #log.info("Engine '%s' was succesfully initialized", name)
        except:
            raise#log.error("Failed to initialize engine '%s'", name)

class TestRecipeAtPythonDocs(TestEngineManager):
    def setUp(self):
        self.em = CustomDeprecatedEngineManager()

