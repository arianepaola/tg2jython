from pylons import c, g, cache, request, session
from pylons.controllers import WSGIController, XMLRPCController
from pylons.controllers.util import abort, redirect_to, etag_cache
from pylons.decorators import jsonify, validate
from pylons.templating import render, render_response
from pylons.i18n import N_, _, ungettext
import projectname.model as model
import projectname.lib.helpers as h

class BaseController(WSGIController):
    def __call__(self, environ, start_response):
        # Insert any code to be run per request here. The Routes match
        # is under environ['pylons.routes_dict'] should you want to check
        # the action or route vars here
        return WSGIController.__call__(self, environ, start_response)

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
