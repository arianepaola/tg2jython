"""
Sprockets Module

This is sort of like the central nervous system of dbsprockets.  Views and
Sessions are collected in separate caches and served up as sprockets.
The cache objects may be solidified at some point with a parent class.
They work for right now.


Classes:
Name           Description
Sprockets      A cache of Sprockets
Sprocket       A binding of Session and View configs
Views          A cache of Views
Sessions       A cache of Sessions

Exceptions:
SessionConfigError
ViewConfigError

Functions:
None

Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
import types

from dbsprockets.viewfactory import ViewFactory
from dbsprockets.viewconfig import *
from dbsprockets.sessionconfig import *
from dbsprockets.saprovider import SAProvider
from dbsprockets.iprovider import IProvider
from dbsprockets.metadata import *
from dbsprockets.view import View

class SessionConfigError(Exception):pass
class ViewConfigError(Exception):pass

class Views(dict):
    def __init__(self, provider, controller):
        if not isinstance(provider, IProvider):
            raise TypeError('provider is not of type IProvider')
        if not isinstance(controller, types.StringTypes):
            raise TypeError('controller is not of type String')
        self.viewFactory = ViewFactory()
        self.provider = provider
        self.controller = controller
        
    defaultViewConfigs = {'databaseView': DatabaseViewConfig,
                          'editRecord'  : EditRecordViewConfig,
                          'addRecord'   : AddRecordViewConfig,
                          #'viewRecord'  : ViewConfig,
                          'tableView'   : TableViewConfig,
                          'tableDef'    : TableDefViewConfig,
                          }

    def _getView(self, key):
        if '__' not in key:
            identifier = ''
            viewType = key
        else:
            viewType, identifier = key.split('__')
        if viewType not in self.defaultViewConfigs:
            raise ViewConfigError('viewType:%s now found in default Views'%viewType)
        viewConfig = self.defaultViewConfigs[viewType](self.provider, identifier, self.controller)
        self[key] = self.viewFactory.create(viewConfig, id=key)
        return self[key]
    
    def __getitem__(self, key):
        if dict.__contains__(self, key):
            return dict.__getitem__(self, key)
        view = self._getView(key)
        self[key] = view
        return view

    def __setitem__(self, key, item):
        if not isinstance(item, View):
            raise TypeError('item must be of type View')
        return dict.__setitem__(self, key, item)
    
class Sessions(dict):
    def __init__(self, provider):
        if not isinstance(provider, IProvider):
            raise TypeError('provider is not of type IProvider')
        self.provider = provider

    defaultSessionConfigs = { 'databaseView': DatabaseSessionConfig,
                              'tableDef'    : SessionConfig,
                              'viewRecord'  : SessionConfig,
                              'tableView'   : TableViewSessionConfig,
                              'editRecord'  : EditRecordSessionConfig,
                              'addRecord'   : AddRecordSessionConfig,
                             }

    def __getitem__(self, key):
        if dict.__contains__(self, key):
            return dict.__getitem__(self, key)
        session = self._getSession(key)
        self[key] = session
        return session

    def _getSession(self, key):
        if '__' not in key:
            identifier = ''
            viewType = key
        else:
            viewType, identifier = key.split('__')
        if viewType in self.defaultSessionConfigs:
            return self.defaultSessionConfigs[viewType](key, self.provider, identifier)
        raise SessionConfigError('Unknown session type')

    def __setitem__(self, key, item):
        if not isinstance(item, SessionConfig):
            raise TypeError('item must be of type SessionConfig')
        return dict.__setitem__(self, key, item)

class Sprocket:
    def __init__(self, view, session):
            
        if not isinstance(view, View):
            raise TypeError('view is not of type View')
        if not isinstance(session, SessionConfig):
            raise TypeError('session is not of type SessionConfig')
        self.session = session
        self.view = view

class Sprockets(dict):
    def __init__(self, provider, controller):
        if not isinstance(provider, IProvider):
            raise TypeError('provider is not of type IProvider')
        if not isinstance(controller, types.StringTypes):
            raise TypeError('controller is not of type String')
        self.views = Views(provider, controller)
        self.sessions = Sessions(provider)
        self.controller = controller

    def __getitem__(self, key):
        if key in self:
            return dict.__getitem__(self, key)
        sprocket = self.getSprocket(key)
        self[key] = sprocket
        return sprocket

    def getSprocket(self, key):
        view = self.views[key]
        session = self.sessions[key]
        return Sprocket(view, session)

    def __setitem__(self, key, item):
        if not isinstance(item, Sprocket):
            raise TypeError('item must be of type Sprocket')
        return dict.__setitem__(self, key, item)
