"""
Simple web.py app using ToscaWidgets and tw.forms
"""
from pprint import pformat
from pkg_resources import require
require('tw.forms', 'Genshi')

import web
from formencode import Invalid
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

# The web.py app
class formcontroller:
    def GET(self):
        # It is very important to set the Content-Type header properly because
        # if it is not text/html (or application/xhtml) TW's middleware will
        # not attempt to inject resources.
        web.header('Content-Type', 'text/html')
        form_output = myform.display(Person())
        print template % locals()

    def POST(self):
        try:
            form_data = myform.validate(web.input())
        except Invalid:
            # Re-display errors and previous input values
            web.header('Content-Type', 'text/html')
            form_output = myform.display()
            print template % locals()
        else:
            web.header('Content-Type', 'text/plain')
            print pformat(form_data)
            

if __name__ == "__main__":
    web.webapi.internalerror = web.debugerror
    web.run(('/', 'formcontroller'), globals(), tw.api.make_middleware)
