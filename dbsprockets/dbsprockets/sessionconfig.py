"""
SessionConfig Module

The SessionConfig defines all of the Data related issues for dbsprockets

Classes:
Name                               Description
SessionConfig                      Parent Class
DatabaseSessionConfig
TableViewSessionConfig
AddRecordViewConfig
EditRecordSessionConfig

Exceptions:
None

Functions:
None

Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""
from cStringIO import StringIO
import types
from iprovider import IProvider
from dbsprockets.metadata import Metadata, DatabaseMetadata, FieldsMetadata, FieldMetadata
from dbsprockets.util import MultiDict, Label

class SessionConfig(object):
    metadataType = Metadata
    def __init__(self, id, provider, identifier=None):
        if not isinstance(id, types.StringTypes):
            raise TypeError('id is not a string')
        if not isinstance(provider, IProvider):
            raise TypeError('provider is not of type IProvider')
        if identifier is not None and not isinstance(identifier, types.StringTypes):
            raise TypeError('identifier is not a string')
        self.id = id
        self.provider = provider
        self.identifier = identifier
        self.metadata = self.metadataType(provider, identifier)

    def getValue(self, values={}):
        """get the value associated with the session
        Arguments:
        values : as provided from the browser
        """
        values = self._doGetValue(values=values)
        return values

    def getCount(self, values={}):
        return self._doGetCount(values)
    
    def _doGetCount(self, values={}):
        raise NotImplementedError
    
    def _doGetValue(self, values={}):
        #the default getValue is just a pass through
        return values

class DatabaseSessionConfig(SessionConfig):
    metadataType = DatabaseMetadata
    
    def _doGetValue(self, values={}):
        r = {}
        tables = self.metadata.keys()
        for table in tables:
            r[table] = self.metadata[table]
        return r

class TableViewSessionConfig(SessionConfig):
    metadataType = FieldsMetadata
    foreignKeyFieldLabels = ['name', '_name', 'description', '_description', 'title']
    
    def _doGetForeignKeyDict(self):
        return self.provider.getForeignKeyDict(self.identifier, self.foreignKeyFieldLabels)
    
    #for this class it makes a lot of sense to override the parent method
    def getValue(self, values={}, page=1, recordsPerPage=20):   
        manyToManyTables = self.provider.getAssociationTables(self.identifier)
        tableName = self.identifier
        offset = (page - 1)*recordsPerPage
        rows = self.provider.select(tableName, resultOffset=offset, resultLimit=recordsPerPage)
        #this is probably going to have to be changed (too slow)
        foreignKeyDict = self._doGetForeignKeyDict()
        primaryKeys=self.provider.getPrimaryKeys(self.identifier)
        newRows = rows
        if len(rows) > 0:
            newRows = []
            for row in rows:
                d = {}
                for key in row.keys():
                    value = row[key]
                    d[key] = value
                    if key == 'password':
                        d[key] = '*'*6
                    if value is not None and key in foreignKeyDict and value in foreignKeyDict[key]:# and not key in primaryKeys:
                        d[key] = Label(foreignKeyDict[key][value])
                        d[key].original=value
                    if self.provider.isBinaryColumn(self.identifier, key):
                        d[key] = '<file>'
                        if row[key] is None:
                            d[key] = ''

                if self.identifier not in manyToManyTables:
                    manyToManyColumns = self.provider.getManyToManyColumns(self.identifier)
                    for column in manyToManyColumns:
                        tableName = column[:-1] #strip off the 's'
                        manyToManyTable = self.provider.getManyToManyTable(self.identifier, tableName)
                        sourcePK = self.provider.getPrimaryKeys(self.identifier)[0]
                        values = {sourcePK:row[sourcePK]}
                        viewColumn = self.provider.getViewColumnName(tableName)
                        idColumn   = self.provider.getPrimaryKeys(tableName)[0]
                        selectedThings = self.provider.select(manyToManyTable, values=values, columnsLimit=[idColumn,])
                        values = MultiDict()
                        for item in selectedThings:
                            values[idColumn] = item[idColumn]
                        manyToManyRows = []
                        if len(selectedThings) != 0:
                            manyToManyRows = self.provider.select(tableName, values=values, whereclauseJoin='or', columnsLimit=[viewColumn,])
                        manyToManyLabels = ''
                        for value in manyToManyRows:
                            manyToManyLabels += unicode(value[viewColumn]) +', '
                        manyToManyLabels = manyToManyLabels[:-2]
                        d[column] = manyToManyLabels
                newRows.append(d)
            
        return newRows
    
    def _doGetCount(self, values={}):
        return self.provider.count(self.identifier)
        
    
class AddRecordSessionConfig(SessionConfig):
    metadataType = FieldsMetadata
    
    def _doGetValue(self, values={}):
        #attach the tablename to the  values
        values['tableName'] = self.metadata.identifier
        values['dbsprockets_id'] =  self.id
        return values
    
class EditRecordSessionConfig(AddRecordSessionConfig):
    metadataType = FieldsMetadata
    
    def _doGetManyToMany(self, values={}):
        #most of this should probably go in provider
        tableName = self.identifier
        pk = self.provider.getPrimaryKeys(tableName)[0]
        srcTable = self.provider.getTable(tableName)

        associationTables = self.provider.getAssociationTables(tableName)
        for table in associationTables:
            table = self.provider.getTable(table)
            srcColumn, dstColumn = table.c
            if srcColumn.foreign_keys[0].column.table != srcTable:
                temp = srcColumn
                srcColumn = dstColumn
                dstColumn = temp
                table = srcColumn.table
            d = {srcColumn.name:values[str(pk)]}
            rows = self.provider.select(table.name, values=d)
            newValues = [row[dstColumn] for row in rows]
            values[str('many_many_'+dstColumn.foreign_keys[0].column.table.name)] = newValues
        return values
    
    def _doGetValue(self, values={}):
        if self.identifier not in self.provider.getManyToManyTables():
            values.update(self._doGetManyToMany(values))
        values = super(EditRecordSessionConfig, self)._doGetValue(values)
        #sql object is not attachable, but a dictionary is

        row = self.provider.selectOnPks(tableName=self.identifier, values=values)[0]
        values.update(row)
        return values