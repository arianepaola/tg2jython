import turbogears as tg
from turbogears import controllers, expose, flash
# from bbwi import model
from turbogears import identity, redirect
from cherrypy import request, response
from create_bt import BuildTaskController
from create_bt_func import BuildTaskFuncController
# from bbwi import json
# import logging
# log = logging.getLogger("bbwi.controllers")

class Root(controllers.RootController):
    buildtasks = BuildTaskController()
    buildtask_function = BuildTaskFuncController()
    @expose(template="bbwi.templates.start")
    # @identity.require(identity.in_group("admin"))
    def index(self):
        return dict()

    @expose(template="bbwi.templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):

        if not identity.current.anonymous and identity.was_login_attempted() \
                and not identity.get_identity_errors():
            redirect(tg.url(forward_url or previous_url or '/', kw))

        forward_url = None
        previous_url = request.path

        if identity.was_login_attempted():
            msg = _("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
        elif identity.get_identity_errors():
            msg = _("You must provide your credentials before accessing "
                   "this resource.")
        else:
            msg = _("Please log in.")
            forward_url = request.headers.get("Referer", "/")

        response.status = 403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
            original_parameters=request.params, forward_url=forward_url)

    @expose()
    def logout(self):
        identity.current.logout()
        redirect("/")
    
    
    