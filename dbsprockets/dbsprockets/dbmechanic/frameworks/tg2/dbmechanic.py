"""
dbmechanic Module

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
from tg.decorators import expose
from tg.controllers import redirect
from tw.api import Widget, CSSLink
import pylons

from dbsprockets.sprockets import Sprockets
from tg import TGController
from dbsprockets.decorators import crudErrorCatcher, validate

dbsprocketsCss = CSSLink(modname='dbsprockets', filename='dbmechanic/static/css/dbmechanic.css')

class BaseController(TGController):
    """Basis TurboGears controller class which is derived from
    TGController
    """

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        # Create a container to send widgets to the template. Only those sent
        # in here will have their resources automatically included in the
        # template
        context.w = WidgetBunch()
        context.css = dbsprocketsCss
        try:
            return TGController.__call__(self, environ, start_response)
        finally:
            pass
            #after everything is done clear out the Database Session
            #so to eliminate possible cross request DBSession polution.
            #model.DBSession.remove()

class DBMechanic(BaseController):
    sprockets = None
    def __init__(self, provider, controller, *args, **kwargs):
        self.provider = provider
        self.sprockets = Sprockets(provider, controller)
        self.controller = controller

        #commonly used views
        sprocket = self.sprockets['databaseView']
        self.databaseValue = sprocket.session.getValue()
        self.databaseView  = sprocket.view.widget
        self.databaseDict  = dict(databaseValue=self.databaseValue, controller=self.controller)
        BaseController.__init__(self, *args, **kwargs)

    @expose('genshi:dbsprockets.dbmechanic.frameworks.tg2.templates.index')
    def index(self):
        pylons.c.databaseView  = self.databaseView
        pylons.c.mainView=Widget("widget")
        return self.databaseDict

    @expose('genshi:dbsprockets.dbmechanic.frameworks.tg2.templates.edit')
    def tableDef(self, tableName):
        sprocket  = self.sprockets['tableDef__'+tableName]
        pylons.c.mainView  = sprocket.view.widget
        pylons.c.databaseView  = self.databaseView
        mainValue = sprocket.session.getValue()
        d = dict(tableName=tableName, mainValue=mainValue)
        d.update(self.databaseDict)
        return d

    @expose('genshi:dbsprockets.dbmechanic.frameworks.tg2.templates.tableView')
    def tableView(self, tableName, page=1, recordsPerPage=25, **kw):
        #this should probably be a decorator
        page = int(page)
        recordsPerPage = int(recordsPerPage)

        sprocket  = self.sprockets['tableView__'+tableName]
        pylons.c.mainView  = sprocket.view.widget
        pylons.c.databaseView  = self.databaseView
        mainValue = sprocket.session.getValue(values=kw, page=page, recordsPerPage=recordsPerPage)
        mainCount = sprocket.session.getCount(values=kw,)
        d = dict(tableName=tableName, mainValue=mainValue, mainCount=mainCount)
        d.update(self.databaseDict)
        d['page'] = page
        d['recordsPerPage'] = recordsPerPage
        return d

    @expose('genshi:dbsprockets.dbmechanic.frameworks.tg2.templates.edit')
    def addRecord(self, tableName, **kw):
        sprocket = self.sprockets['addRecord__'+tableName]
        pylons.c.mainView  = sprocket.view.widget
        pylons.c.databaseView  = self.databaseView
        mainValue = sprocket.session.getValue(values=kw)
        d = dict(tableName=tableName, mainValue=mainValue)
        d.update(self.databaseDict)
        return d

    @expose('genshi:dbsprockets.dbmechanic.frameworks.tg2.templates.edit')
    def editRecord(self, tableName, **kw):
        sprocket = self.sprockets['editRecord__'+tableName]
        pylons.c.mainView  = sprocket.view.widget
        pylons.c.databaseView  = self.databaseView
        mainValue = sprocket.session.getValue(values=kw)
        d = dict(tableName=tableName, mainValue=mainValue)
        d.update(self.databaseDict)
        return d

    def createRelationships(self, tableName, params):
        #this might become a decorator
        #check to see if the table is a many-to-many table first
        if tableName in self.provider.getManyToManyTables():
            return
        #right now many-to-many only supports single primary keys
        pk=self.provider.getPrimaryKeys(tableName)
        assert len(pk)==1
        id = params[pk[0]]
        relationships = {}
        for key, value in params.iteritems():
            if key.startswith('many_many_'):
                relationships.setdefault(key[10:], []).append(value)
        for key, value in relationships.iteritems():
            self.provider.setManyToMany(tableName, id, key, value)

    @expose()
    @validate(error_handler=editRecord)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.IntegrityError, error_handler='editRecord')
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.ProgrammingError, error_handler='editRecord')
    def edit(self, tableName, *args, **kw):
        params = pylons.request.params.copy()
        self.createRelationships(tableName, params)

        self.provider.edit(tableName, values=kw)
        redirect(self.controller+'/tableView/'+tableName)

    @expose()
    @validate(error_handler=addRecord)
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.IntegrityError, error_handler='addRecord')
    @crudErrorCatcher(errorType=sqlalchemy.exceptions.ProgrammingError, error_handler='addRecord')
    def add(self, tableName, **kw):
        params = pylons.request.params.copy()
        self.createRelationships(tableName, params)

        self.provider.add(tableName, values=kw)
        redirect(self.controller+'/tableView/'+tableName)

    @expose()
    def delete(self, tableName, **kw):
        self.provider.delete(tableName, values=kw)
        redirect(self.controller+'/tableView/'+tableName)
