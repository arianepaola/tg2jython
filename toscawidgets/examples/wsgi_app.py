"""
Simple WSGI app using Paste and ToscaWidgets

Based on script by James Gardner
"""
from wsgiref.simple_server import make_server
from wsgiref.validate import validator
from pprint import pformat, pprint
from optparse import OptionParser

from pkg_resources import require
require('tw.forms', 'WebOb', 'Genshi')

from formencode import Invalid
from webob import Request, Response

import tw.api
from tw.forms.samples import AddUserForm

template = """\
<html xmlns="http://www.w3.org/1999/xhtml">
  <head><title>Simple WSGI app using tw.forms and ToscaWidgets</title></head>
  <body>%(form_output)s</body>
</html>
"""

# Dummy model objects to prefill the form.
class Address(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

class Person(object):
    name = "Peter"
    email = "peter@example"
    age = 2
    address = [Address(street="Elm Street")]

# The form instance. Note that widgets are usually module-level singletons.
# Once initialized they are state-less so they are safe to use in several
# threads while serving concurrent requests.
myform = AddUserForm('form')

# The WSGI app
def app(environ, start_response):
    req = Request(environ)
    resp = Response(request=req, content_type="text/html; charset=UTF8")
    if req.POST:
        try:
            value = myform.validate(req.POST)
            resp.body = ('<h1>Validated data:</h1>'
                         '<pre>%s</pre>'
                         '<a href="./">Again</a>' % pformat(value))
            return resp(environ, start_response)
        except Invalid, error:
            pass
    # Note that if validation errors and values are passed via request-local
    # storage so the form displays them.
    # Errors (the Invalid exception instance) can also be passed explicitly as
    # the 'error' keyword argument when displaying a form.
    form_output = myform.display(Person())
    resp.body = (template % locals()).encode('utf-8')
    return resp(environ, start_response)

# Used to validate TW's middleware WSGI compliance
app = validator(app)

# Stack TW's middleware
app = tw.api.make_middleware(app, stack_registry=True)

# Used to validate TW's middleware WSGI compliance
app = validator(app)


if __name__ == "__main__":
    try:
        from weberror.evalexception import EvalException
        app = EvalException(app)
    except ImportError:
        print "WebError is not available for debugging"
    server = make_server('', 8000, app)
    print "Server started at http://127.0.0.1:8000/"
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
