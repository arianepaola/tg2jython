"""
dbmechanic Module (tg1 compat)

this contains a turbogears controller which allows the user to have a 
phpMyAdmin *cringe*-like interface.  It is intended to be a replacement
for Catwalk

Classes:
Name                               Description
DBMechanic

Exceptions:
None

Functions:
None

Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
import sqlalchemy
import cherrypy
from tw.api import Widget, CSSLink, Link


try:
    from turbogears.controllers import Controller
    from turbogears import expose, redirect, validate, error_handler
    import turbogears
    #register the cherrypy static directory for the image and css files.
    def add_custom_stdvars(vars):
        return vars.update({"dbmech_css": dbMechanicCss,
                            "dbmech_footer_img": dbMechanicFooterImg,
                           })
    
    turbogears.view.variable_providers.append(add_custom_stdvars)
except ImportError:
    # when nosetests is going through package discovery, it hits this module.
    # since there is not turbogears application running in this python instance
    # it crashes saying that turbgears.config is not defined.
    # we do this so that nosetests can load a dummy version of this module and keep on trucking.
    class Controller: pass
    def expose(*args, **kw):
        return lambda *args, **kw: None
    def error_handler(*args, **kw):
        return lambda *args, **kw: None
    def validate(*args, **kw):
        return lambda *args, **kw: None

from tw.api import Widget
from dbsprockets.sprockets import Sprockets
from dbsprockets.saprovider import SAProvider
#from dbsprockets.validator import validate, crudErrorCatcher

from dbsprockets.dbmechanic.resources import dbMechanicCss, dbMechanicFooterImg



def getSprocket(self):
    request = cherrypy.request
    sprocket = self.sprockets[request.params['dbsprockets_id']]
    form = sprocket.view.widget
    return form

class DBMechanic(Controller):
    def __init__(self, provider, controller, *args, **kwargs):
        self.provider = provider
        self.sprockets = Sprockets(provider, controller)
        self.controller = controller
        
        #commonly used views
        sprocket = self.sprockets['databaseView']
        self.databaseValue = sprocket.session.getValue()
        self.databaseView  = sprocket.view.widget
        self.databaseDict  = dict(databaseView=self.databaseView, databaseValue=self.databaseValue, controller=self.controller)#, databaseView=self.databaseView, databaseValue=self.databaseValue)
        

    @expose('genshi:dbsprockets.dbmechanic.frameworks.tg.templates.index')
    def index(self):
        d = dict(mainView=Widget("widget"), mainValue = {}, tableName='')
        d.update(self.databaseDict)
        return d


    @expose('genshi:dbsprockets.dbmechanic.frameworks.tg.templates.index')
    def tableDef(self, tableName):
        sprocket  = self.sprockets['tableDef__'+tableName]
        mainValue = sprocket.session.getValue()
        d = dict(tableName=tableName, mainView=sprocket.view.widget, mainValue=mainValue)
        d.update(self.databaseDict)
        return d
    
    @expose('genshi:dbsprockets.dbmechanic.frameworks.tg.templates.tableView')
    def tableView(self, tableName, page=1, recordsPerPage=25, **kw):
        #this should probably be a decorator 
        page = int(page)
        recordsPerPage = int(recordsPerPage)
        
        sprocket  = self.sprockets['tableView__'+tableName]
        mainValue = sprocket.session.getValue(values=kw, page=page, recordsPerPage=recordsPerPage)
        mainCount = sprocket.session.getCount(values=kw)
        d = dict(tableName=tableName, mainView=sprocket.view.widget, mainValue=mainValue, mainCount=mainCount)
        d.update(self.databaseDict)
        d['page'] = page
        d['recordsPerPage'] = recordsPerPage
        return d
    
    @expose('genshi:dbsprockets.dbmechanic.frameworks.tg.templates.index')
    def addRecord(self, tableName, **kw):
        sprocket = self.sprockets['addRecord__'+tableName]
        mainValue = sprocket.session.getValue(values=kw)
        d = dict(tableName=tableName, mainView=sprocket.view.widget, mainValue=mainValue)
        d.update(self.databaseDict)
        return d
    
    @expose('genshi:dbsprockets.dbmechanic.frameworks.tg.templates.index')
    def editRecord(self, tableName, **kw):
        sprocket = self.sprockets['editRecord__'+tableName]
        mainValue = sprocket.session.getValue(values=kw)
        d = dict(tableName=tableName, mainView=sprocket.view.widget, mainValue=mainValue)
        d.update(self.databaseDict)
        return d
    
    def createRelationships(self, tableName, params):
        #this might become a decorator
        #check to see if the table is a many-to-many table first
        if tableName in self.provider.getManyToManyTables():
            return
        #right now many-to-many only supports single primary keys
        params = cherrypy.request.params
        id = params[self.provider.getPrimaryKeys(tableName)[0]]
        relationships = {}
        for key, value in params.iteritems():
            if key.startswith('many_many_'):
                relationships.setdefault(key[10:], []).append(value)
        for key, value in relationships.iteritems():
            self.provider.setManyToMany(tableName, id, key, value)
    
    @expose()
    @validate(getSprocket)
#    @crudErrorCatcher(errorType=sqlalchemy.exceptions.IntegrityError, error_handler='editRecord')
    @error_handler(editRecord)
    def edit(self, tableName, *args, **kw):
        params = cherrypy.request
        self.createRelationships(tableName, params)

        self.provider.edit(tableName, values=kw)
        raise redirect(self.controller+'/tableView/'+tableName)

    @expose()
    @validate(getSprocket)
    @error_handler(addRecord)
#    @crudErrorCatcher(errorType=sqlalchemy.exceptions.IntegrityError, error_handler='addRecord')
    def add(self, tableName, **kw):
        params = cherrypy.request
        self.createRelationships(tableName, params)

        self.provider.add(tableName, values=kw)
        raise redirect(self.controller+'/tableView/'+tableName)

    @expose()
    def delete(self, tableName, **kw):
        self.provider.delete(tableName, values=kw)
        raise redirect(self.controller+'/tableView/'+tableName)
    