"""
dbmechanic module for Pylons

Initial version by Isaac Csandl <nerkles _at_ gmail {d0t} com> based on the tg2 version.

"""
import os
import pkg_resources
import sqlalchemy
from tw.api import Widget
import pylons
from pylons.templating import cached_template, pylons_globals
from pylons.controllers import WSGIController
from pylons import c, request
from dbsprockets.sprockets import Sprockets
#from dbsprockets.decorators import crudErrorCatcher, validate
from tw.api import WidgetBunch
from genshi.template import TemplateLoader


def render_genshi(template_name, genshi_loader, cache_key=None, cache_type=None,
                  cache_expire=None, fragment=False, format='xhtml'):
    """
    Copied out of Pylons so that we can specify the path to genshi templates.
    
    Render a template with Genshi
    
    Accepts the cache options ``cache_key``, ``cache_type``, and
    ``cache_expire`` in addition to fragment and format which are
    passed to Genshi's render function.
    
    """
    # Create a render callable for the cache function
    def render_template():
        # First, get the globals
        globs = pylons_globals()
        
        # Grab a template reference
        template = genshi_loader.load(template_name)
        
        return template.generate(**globs).render()
    
    return cached_template(template_name, render_template, cache_key=cache_key,
                           cache_type=cache_type, cache_expire=cache_expire,
                           ns_options=('fragment', 'format'),
                           fragment=fragment, format=format)


class DBMechanic(WSGIController):
    sprockets = None
    def __init__(self, provider, controller, *args, **kwargs):
        self.provider = provider
        self.sprockets = Sprockets(provider, controller)
        self.controller = controller
        #commonly used views
        c.w = WidgetBunch()
        sprocket = self.sprockets['databaseView']
        self.databaseValue = sprocket.session.getValue()
        self.databaseView  = sprocket.view.widget
        print 'controller:', self.controller
        
        self.databaseDict  = dict(controller=self.controller)
        self.genshi_loader = TemplateLoader([pkg_resources.resource_filename('dbsprockets.dbmechanic.frameworks.pylons', 'templates')])
        WSGIController.__init__(self, *args, **kwargs)
    
    def index(self):
        c.w.databaseView  = self.databaseView
        c.w.mainView=Widget("widget")
        return render_genshi('index.html', self.genshi_loader)

    
    def tableDef(self, id): #tableName):
        c.tableName = id
        sprocket  = self.sprockets['tableDef__'+c.tableName]
        c.w.mainView  = sprocket.view.widget
        c.w.databaseView  = self.databaseView
        c.mainValue = sprocket.session.getValue()
        for key, value in self.databaseDict.iteritems():
            setattr(c, key, value)
        return render_genshi('index.html', self.genshi_loader)
    
    def tableView(self, id):
        c.tableName = id
        c.page = request.params.get('page', 1)
        c.recordsPerPage = request.params.get('recordsPerPage', 25)
        #this should probably be a decorator
        c.page = int(c.page)
        c.recordsPerPage = int(c.recordsPerPage)
        sprocket  = self.sprockets['tableView__'+c.tableName]
        c.w.mainView  = sprocket.view.widget
        c.w.databaseView  = self.databaseView
        c.mainValue = sprocket.session.getValue(values=request.params, page=c.page, recordsPerPage=c.recordsPerPage)
        c.mainCount = sprocket.session.getCount(values=request.params)
        for key, value in self.databaseDict.iteritems():
            setattr(c, key, value)
        return render_genshi('tableView.html', self.genshi_loader)
    
    def addRecord(self, id): #tableName, **kw):
        c.tableName = id
        sprocket = self.sprockets['addRecord__'+c.tableName]
        c.w.mainView  = sprocket.view.widget
        c.w.databaseView  = self.databaseView
        kw = {}
        for key, value in request.params.iteritems():
            if key and value:
                setattr(kw, key, value)
        c.mainValue = sprocket.session.getValue(values=kw)
        for key, value in self.databaseDict.iteritems():
            setattr(c, key, value)
        return render_genshi('index.html', self.genshi_loader)
    
    def editRecord(self, id): #tableName, **kw):
        c.tableName = request.params.get('tableName', None)
        sprocket = self.sprockets['editRecord__'+c.tableName]
        c.w.mainView  = sprocket.view.widget
        c.w.databaseView  = self.databaseView
        kw = {}
        kw.update(request.params.__dict__)
        c.mainValue = sprocket.session.getValue(values=kw)
        for key, value in self.databaseDict.iteritems():
            setattr(c, key, value)
        return render_genshi('index.html', self.genshi_loader)
    
    def _createRelationships(self, tableName, params):
        #this might become a decorator
        #check to see if the table is a many-to-many table first
        if tableName in self.provider.getManyToManyTables():
            return
        #right now many-to-many only supports single primary keys
        id = params[self.provider.getPrimaryKeys(tableName)[0]]
        relationships = {}
        for key, value in params.iteritems():
            if key.startswith('many_many_'):
                relationships.setdefault(key[10:], []).append(value)
        for key, value in relationships.iteritems():
            self.provider.setManyToMany(tableName, id, key, value)
    
    # @validate(error_handler=editRecord)
    #@crudErrorCatcher(errorType=sqlalchemy.exceptions.IntegrityError, error_handler='editRecord')
    #@crudErrorCatcher(errorType=sqlalchemy.exceptions.ProgrammingError, error_handler='editRecord')
    def edit(self, id): # tableName, *args, **kw):
        tableName = request.params.get('tableName', None)
        params = pylons.request.params.copy()
        self._createRelationships(tableName, params)
        self.provider.edit(tableName, values=params)
        raise redirect(self.controller+'/tableView/'+tableName)
    
    # @validate(error_handler=addRecord)
    #@crudErrorCatcher(errorType=sqlalchemy.exceptions.IntegrityError, error_handler='addRecord')
    #@crudErrorCatcher(errorType=sqlalchemy.exceptions.ProgrammingError, error_handler='addRecord')
    def add(self, id): #tableName, **kw):
        tableName = request.params.get('tableName', None)
        params = pylons.request.params.copy()
        self._createRelationships(tableName, params)
        self.provider.add(tableName, values=params)
        raise redirect(self.controller+'/tableView/'+tableName)
    
    def delete(self, id): # tableName, **kw):
        tableName = request.params.get('tableName', None)
        self.provider.delete(tableName, values=kw)
        raise redirect(self.controller+'/tableView/'+tableName)
