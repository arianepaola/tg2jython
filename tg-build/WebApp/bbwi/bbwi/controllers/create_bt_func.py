import logging

import cherrypy as cp
import turbogears as tg
from turbogears import controllers, expose, flash
from turbogears import identity, redirect

from bbwi.model import BuildSteps, BuildStep, BuildTask, BuildTaskFuncs
from bbwi.source_generators.gen_buildtask import GenerateBuildTask
from bbwi.forms import DynamicForm, OverviewForm

log = logging.getLogger('bbwi.controller')

class BuildTaskFuncController(controllers.Controller):
    
    @expose(template="bbwi.templates.create_bt_func")
    def new(self, **kw):
        try:
            bt = cp.session['build_task']
        except KeyError:
            cp.session['build_task'] = BuildTask()

            
        return dict(show_form=False, buildtask_funcs = BuildTaskFuncs.select())
    index = new