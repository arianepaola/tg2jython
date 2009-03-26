import pprint
import turbogears as tg
from turbogears import controllers, expose, flash, validate, error_handler

from tw.forms.samples import AddUserForm

form = AddUserForm("myform")

# A dummy model object we send to the form to pre-populate it
class Person(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

class Root(controllers.RootController):
    @expose(template="tg1sample.templates.welcome")
    def index(self):
        import time
        flash("Your application is now running")
        # you could also import form from the template
        return dict(now=time.ctime(), form=form, person=Person(name="John Doe"))


    # Tells turbogears to call index() if validation fails
    @error_handler(index)
    # Tells turbogears to validate input with the form
    @validate(form)
    @expose()
    def process_form(self, **kw):
        return pprint.pformat(kw)

