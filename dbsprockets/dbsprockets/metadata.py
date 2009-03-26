"""
matadata Module

this contains the class which definies the generic interface for metadata
that is used in form generation later in the pipeline

Classes:
Name                               Description
Metadata                           general metadata function
DatabaseMetadata                   describes the fields as entries in the dictionary
FieldsMetadata                     describes the columns as entries in the dictionary
FieldMetadata                      generic type this is not used right now.

Exceptions:
MetadataError

Functions:
None

Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
from dbsprockets.iprovider import IProvider

class MetadataError(Exception):pass
class NotFoundError(Exception):pass

class Metadata(dict):
    """
    """
    def __init__(self, provider, identifier=None):
        if not isinstance(provider, IProvider):
            raise TypeError('provider must be of type IProvider not %s'%type(provider))
        self.provider = provider
        self.identifier=identifier
        
    def __setitem__(self, key, value):
        self._doCheckSetItem(key, value)
        dict.__setitem__(self, key, value)

    def __getitem__(self, item):
        try:
            value = self._doGetItem(item)
            return value
        except NotFoundError:
            return dict.__getitem__(self, item)

    def keys(self):
        r = self._doKeys()
        r.extend(dict.keys(self))
        return r
    def primaryKeys(self):
        return self._doGetPrimaryKeys()
    
    @property
    def foreignKeys(self):
        return self._doGetForeignKeys()
    
    @property
    def autoIncrementFields(self):
        return self._doGetAutoIncrementFields()
    
    def _doGetAutoIncrementFields(self):
        raise NotImplementedError
    def _doGetForeignKeys(self):
        raise NotImplementedError
    def _doGetPrimaryKeys(self):
        raise NotImplementedError
    def _doCheckSetItem(self, key, value):
        raise NotImplementedError
    def _doGetItem(self, item):
        raise NotImplementedError
    def _doKeys(self):
        raise NotImplementedError

class DatabaseMetadata(Metadata):
    """
    """
    def __init__(self, provider, identifier=None):
        Metadata.__init__(self, provider, identifier)
        self._tables = None
        
    def _doCheckSetItem(self, key, value):
        if key in self.provider.tables:
            raise MetadataError('%s is already a table name in the database'%key)
        
    def _doGetPrimaryKeys(self):
        return []
    
    def _doGetForeignKeys(self):
        return []

    def _doGetItem(self, item):
        if item in self.provider.tables:
            return self.provider.getTable(item)
        raise NotFoundError

    def _doKeys(self):
        if self._tables is None:
            self._tables = self.provider.getTables()
        return self._tables
    
class FieldsMetadata(Metadata):
    """
    """
    def __init__(self, provider, identifier):
        Metadata.__init__(self, provider, identifier)
        self.table = self.provider.getTable(identifier)

    def _doCheckSetItem(self, key, value):
        if key in self.table.columns:
            raise MetadataError('%s is already found in table: %s'%(key, self.table))

    def _doGetItem(self, item):
        if item in self.table.columns:
            return self.table.columns[item]
        raise NotFoundError

    def _doGetAutoIncrementFields(self):
        return self.provider.getAutoIncrementFields(self.identifier)
    
    def _doGetPrimaryKeys(self):
        return self.provider.getPrimaryKeys(self.identifier)
    
    def _doGetForeignKeys(self):
        return [c.name for c in self.provider.getForeignKeys(self.identifier)]
    
    def _doKeys(self):
        r = self.table.columns.keys()
        return r
        
class FieldMetadata(Metadata):
    """
    """
    pass

