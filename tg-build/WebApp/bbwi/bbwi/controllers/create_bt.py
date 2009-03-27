import logging

import cherrypy as cp
import turbogears as tg
from turbogears import controllers, expose, flash
from turbogears import identity, redirect

from bbwi.model import BuildSteps, BuildStep, BuildTask
from bbwi.source_generators.gen_buildtask import GenerateBuildTask
from bbwi.forms import DynamicForm, OverviewForm

log = logging.getLogger('bbwi.controller')

param_form = DynamicForm()
ow_form = OverviewForm()

class BuildTaskController(controllers.Controller):
    
    @expose(template="bbwi.templates.create_bt")
    def new(self, **kw):
        try:
            bt = cp.session['build_task']
        except KeyError:
            cp.session['build_task'] = BuildTask()
        try:
            bt_list = cp.session['bt_list']
        except KeyError:
            cp.session['bt_list'] =[]
            
        return dict(show_form=False, buildsteps = BuildSteps.select())
    index = new

    @expose('json')
    def add_bs(self, type=None):
        log.debug("Build step typ: %s", type)
        fields = BuildSteps.byName(type).parameter.split()
        html =  param_form.render(
            name="param_form",
            fields=fields,
            submit_text='Add build step',
            form_attrs=dict(id="param_form"),
            bs_type=type
        )
        return dict(form=html)

    @expose()
    def insert_bs(self,**kwargs):
        bt = cp.session['build_task']
        bs = BuildStep(kwargs['type'])
        del kwargs['type']
        bs.set_parameter(kwargs)
        bt.add_step(bs)
        html = ow_form.render(name="ow_form",
                              fields = bt.build_steps,
                              form_attrs=dict(id="ow_form")
                              )
        return dict(form=html)
    
    @expose('json')
    def finish_bt(self,**kwargs):
        bt = cp.session['build_task']
        bt.set_name(kwargs['bt_name'])
        
        file = open("tgbuilder.py","a+t")
        file.writelines(GenerateBuildTask(bt).generate_source())
        file.close()
        cp.session['bt_list'].append(bt)
        cp.session['build_task'] = BuildTask()
        return {}