from tw.core.view import EngineManager
from tw.core.util import RequestLocalDescriptor, disable_runtime_checks
from tw.core.registry import StackedObjectProxy, Registry

__all__ = ["HostFramework"]

class RequestLocal(object):
    def __init__(self, environ):
        self.environ = environ
        self.resources = {}

class HostFramework(object):
    """
    This class is the interface between ToscaWidgets and the framework or
    web application that's using them.

    The an instance of this class should be passed as second argument to
    :class:`tw.core.middleware.ToscaWidgetsMiddleware` which will call its
    :meth:`start_request` method at the beginning of every
    request and :meth:`end_request` when the request is over so I have a chance
    to register our per-request context.

    A request-local proxy to a configured instance is placed at the beginning
    of the request at :attr:`tw.framework`

    **Constructor's arguments:**

    engines
       An instance of :class:`tw.core.viewEngineManager`.

    default_view
       The name of the template engine used by default in the container app's
       templates. It's used to determine what conversion is neccesary when
       displaying root widgets on a template. 

    translator
       Function used to translate strings.

    enable_runtime_checks
       Enables runtime checks for possible programming errors regarding
       modifying widget attributes once a widget has been initialized.
       Disabling this option can significantly reduce Widget initializatio
       time.

       .. note::
           This operation modifies the Widget class and will affect any
           application using ToscaWidgets in the same process.
    """
    request_local = StackedObjectProxy(name="ToscaWidgets per-request storage")
    request_local_class = RequestLocal

    default_view = RequestLocalDescriptor('default_view', 'toscawidgets')

    def __init__(self, engines=None, default_view='toscawidgets',
                 translator=lambda s: s, enable_runtime_checks=True):
        if engines is None:
            engines = EngineManager()
        self.engines = engines
        self._default_view = default_view
        self.translator = translator
        if not enable_runtime_checks:
            disable_runtime_checks()
    
    def start_request(self, environ):
        """
        Called by the middleware when a request has just begun so I have a
        chance to register the request context Widgets will use for various
        things.
        """
        registry = environ['paste.registry']
        registry.register(self.request_local, self.request_local_class(environ))
        self.request_local.default_view = self._default_view

    def end_request(self, environ):
        """
        Called by the middleware when a request has just finished so I can
        clean up.
        """
        pass

    def url(self, url):
        """
        Returns the absolute path for the given url.
        """
        prefix = self.request_local.environ['toscawidgets.prefix']
        script_name = self.request_local.environ['SCRIPT_NAME']
        return ''.join([script_name, prefix, url])

    def register_resources(self, resources):
        """
        Registers resources for injection in the current request.
        """
        from tw.api import merge_resources
        merge_resources(self.request_local.resources, resources)

    def pop_resources(self):
        """
        Returns returns the resources that have been registered for this
        request and removes them from request-local storage area.
        """
        resources =  self.request_local.resources
        self.request_local.resources = {}
        return resources
