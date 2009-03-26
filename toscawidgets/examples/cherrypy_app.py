from wsgiref.validate import validator
from pprint import pformat

from pkg_resources import require
require('CherryPy>=3.0.0', 'tw.forms', 'Genshi')

import cherrypy
from genshi.template import Context, MarkupTemplate
from genshi.output import DocType
from formencode import Invalid
from tw.forms.samples import AddUserForm

template = MarkupTemplate("""\
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://genshi.edgewall.org/">
  <head> <title>SimpleWSGI app using tw.forms and ToscaWidgets</title></head>
  <body>${form.display(value)}</body>
</html>
""")

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

class Controller(object):
    def index(self, **form_data):
        if form_data:
            try:
                value = myform.validate(form_data)
                return ('<h1>Validated data:</h1>'
                        '<pre>%s</pre>'
                        '<a href="./">Again</a>' % pformat(value))
            except Invalid, error:
                pass
        ctx = Context(value=Person(), form=myform)
        t = template.generate(ctx)
        cherrypy.response.headers['Content-Type'] = 'text/html; charset=UTF8'
        return  t.render(method='xhtml', doctype=DocType.XHTML)
    index.exposed = True
        

#XXX I'm not sure how can I pass args. to the middleware with CP's config
#    pipeline API, hence this hacky wrapper. Any better way of doing this?
def tw_middleware(app):
    from tw.api import make_middleware
    conf = {'toscawidgets.framework.default_view':'genshi',
            'toscawidgets.middleware.inject_resources': 'true'}
    return make_middleware(app, conf, stack_registry=True)


cp_config = {
    '/': {'wsgi.pipeline': [
	('validator1', validator),
        ('tw', tw_middleware),
	('validator2', validator),
        ]}
}

if __name__ == "__main__":
    cherrypy.quickstart(Controller(), '', cp_config)
