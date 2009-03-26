import pylons
from tg2testapp.lib.base import BaseController
from tg import expose, flash
from pylons.i18n import ugettext as _
from tg import redirect, validate
from tw.forms.fields import PasswordField
from formencode.validators import FieldsMatch
from formencode import Schema

from tg2testapp.model import User, metadata
from dbsprockets.dbmechanic.frameworks.tg2 import DBMechanic
from dbsprockets.saprovider import SAProvider
from dbsprockets.primitives import makeForm, makeTable, getTableValue

requiredFields = ['password', 'user_name', 'email_address']
limitFields  = ['user_name', 'display_name', 'email_address', 'password', ]

additionalFields = [PasswordField('passwordVerification', label_text='Verify'),]
formValidator =  Schema(chained_validators=(FieldsMatch('password',
                                                        'passwordVerification',
                                                        messages={'invalidNoMatch': 
                                                                  "Passwords do not match"}),))

registrationForm = makeForm(User, 
                            'registration', 
                            requiredFields=requiredFields, 
                            limitFields=limitFields, 
                            additionalFields=additionalFields, 
                            formValidator=formValidator)
usersTable       = makeTable(User, '/', omittedFields=['user_id', 'created', 'password'])
loginForm        = makeForm (User, identifier='myLoginForm', action='/login', limitFields=['user_name', 'password'])

class RootController(BaseController):

    dbmechanic = DBMechanic(SAProvider(metadata), '/dbmechanic')

    @expose('sprockets.templates.index')
    def index(self):
        from datetime import datetime
        flash(_("Your application is now running"))
        return dict(now=datetime.now())

    @expose('genshi:sprockets.templates.register')
    def register(self, **kw):
        pylons.c.w.form = registrationForm
        return dict(value=kw)

    @validate(registrationForm, error_handler=register)
    def registration(self, **kw):
        raise redirect('/')

    
    @expose('genshi:sprockets.templates.register')
    def users(self):
        pylons.c.w.form = usersTable
        value = getTableValue(User)
        return dict(value=value)
    
    @expose('genshi:sprockets.templates.register')
    def login(self, **kw):
        pylons.c.w.form = loginForm
        return dict(value=kw)
