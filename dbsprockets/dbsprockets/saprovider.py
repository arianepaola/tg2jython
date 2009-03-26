"""
saprovider Module

this contains the class which allows dbsprockets to interface with sqlalchemy.

Classes:
Name                               Description
SAProvider                         sqlalchemy metadata/crud provider

Exceptions:
None

Functions:
None


Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""

from sqlalchemy import *
from dbsprockets.iprovider import IProvider
from cgi import FieldStorage


class SAProvider(IProvider):
    """A Class to manipulate an sqlalchemy interface.
    
    Functions:
    getTables      get a list of tables from the database
    getTable       get the table definition for a given table
    getColumns     get the columns from a given table
    getPrimaryKeys get the primary keys from a given table.
    
    Attributes:
    metadata       link to the sqlalchemy metadata
    """
    whereclauseJoinFuncs = {'and':and_, 'or':or_}
    
    def __init__(self, metadata):
        if not isinstance(metadata, MetaData):
            raise TypeError('metadata is not of type sqlalchemy.MetaData')
        self.metadata = metadata
        self.tables = {}
        for name, table in metadata.tables.iteritems():
            self.tables[name] = table
        
    def getTables(self):
        """()->[list of tablesNames] 
        get a list of tables from the database"""
        return self.metadata.tables.keys()
    tables = property(getTables)
    
    def getTable(self, name):
        """(name) -> sqlalchemy.schema.Table
        get the table definition with the given table name
        """
        return self.metadata.tables[name]
    
    def getColumns(self, tableName):
        """(name) -> [list of columnNames]
        get the column names given the table name
        """
        return self.metadata.tables[tableName].columns.keys()
    
    def getColumn(self, tableName, name):
        """(tableName, name) -> sqlalchemy.schema.Column
        get the column definition givcen the tablename and column name.
        """
        return self.metadata.tables[tableName].columns[name]
    
    def getPrimaryKeys(self, tableName):
        """(name) -> [list of columnNames that are primary keys]
        get a list of columns which are primary keys
        """
        table = self.getTable(tableName)
        return table.primary_key.keys()

    def getAutoIncrementFields(self, tableName):
        table = self.getTable(tableName)
        return [c.name for c in table.c if c.autoincrement]
    
    def getDefaultValues(self, tableName):
        table = self.getTable(tableName)
        r = {}
        for c in table.c:
            if c.default is not None:
                r[c.name] = c.default.execute()
        return r
    
    def _generateWhereclause(self, table, pks, values={}, join='and'):
        l = [(getattr(table.c, key)==value) for key, value in values.iteritems() if key in pks and hasattr(table.c, key)]
        whereclause = None
        #one primary key
        if len(l) == 1:
            whereclause = l[0]
        #case of multiple keys
        elif len(l) > 1:
            joinFunc = self.whereclauseJoinFuncs[join]
            whereclause = joinFunc(*l)
        return whereclause
    
    def _generateColumnListing(self, table, columnNames):
        l = [getattr(table.c, key) for key in columnNames if hasattr(table.c, key)]
        return l

    def _removePrimaryKeys(self, tableName, values={}):
        for key in self.getPrimaryKeys(tableName):
            if key in values:
                values.pop(key)
        return values
    
    def _removePrimaryKeysIfNotForeign(self, tableName, values={}):
        foreignKeys=[c.name for c in self.getForeignKeys(tableName)]
        for key in self.getPrimaryKeys(tableName):
            if (key in values) and (not (key in foreignKeys)):
                values.pop(key)
        return values
    
    
    def _removeNonLimitColumns(self, values, limit):
        if limit is None:
            return values
        for key in values.keys():
            if key not in limit:
                values.pop(key)
        return values

    def getForeignKeys(self, tableName):
        table = self.getTable(tableName)
        return [column for column in table.columns if len(column.foreign_keys)>0]

    def getForeignKeyDict(self, tableName, foreignKeyFieldLabels=['name', '_name', 'description', '_description', 'title']):
        """Returns a dict of dicts where the keys are the column names, and then the row values.  Something like this:
        {town_table:{1:'Arvada', 2:'Denver', 3:'Golden'}}
        """
        d = {}
        foreignKeyColumns = self.getForeignKeys(tableName)
        for column in foreignKeyColumns:
            table = column.foreign_keys[0].column.table
            foreignTableName = table.name
            rows      = table.select().execute().fetchall()
            if len(rows) == 0:
                d[column.name] = {}
                continue
            viewColumn = self._findFirstColumn(foreignTableName, foreignKeyFieldLabels)
            idColumn   = self._findFirstColumn(foreignTableName, ['_id', 'id'])
            innerD = {}
            for row in rows:
                innerD[row[idColumn]] = row[viewColumn]
            d[column.name] = innerD
        return d
    
    def getManyToManyTables(self):
        if not hasattr(self, '_manyToManyTables'):
            self._manyToManyTables = [table for table in self.tables if len(self.getForeignKeys(table)) == 2 and len(self.getColumns(table)) == 2]
        return self._manyToManyTables

    def getManyToManyColumns(self, tableName):
        table = self.getTable(tableName)
        manyToManyTables = self.getAssociationTables(tableName)
        manyToManyColumns = []
        for manyToManyTable in manyToManyTables:
            column1, column2 = self.getTable(manyToManyTable).columns
            if column1.foreign_keys[0].column.table == table:
                manyToManyColumns.append(column2.foreign_keys[0].column.table.name+'s')
            else:
                manyToManyColumns.append(column1.foreign_keys[0].column.table.name+'s')
        return manyToManyColumns
    
    def getManyToManyTable(self, tableName1, tableName2):
        table1 = self.getTable(tableName1)
        table2 = self.getTable(tableName2)
        for table in self.getManyToManyTables():
            tables = [column.foreign_keys[0].column.table for column in self.getTable(table).columns]
            if table1 in tables and table2 in tables:
                return table
            
    
    def getAssociationTables(self, tableName):
        tables = []
        srcTable = self.getTable(tableName)
        for table in self.getManyToManyTables():
            for column in self.getTable(table).columns:
                key = column.foreign_keys[0]
                if key.column.table is srcTable:
                    tables.append(table)
                    break
        return tables
    
    def setManyToMany(self, srcTableName, srcID, relatedTableName, values):
        srcTable = self.getTable(srcTableName)
        relatedTable = self.getTable(relatedTableName)
        
        manyToManyTables = self.getManyToManyTables()
        foundTable = None
        #find the right table to modify
        for table in manyToManyTables:
            table = self.getTable(table)
            column1, column2 = table.c
            if column1.foreign_keys[0].column.table == srcTable and column2.foreign_keys[0].column.table == relatedTable:
                foundTable = table
                break;
            if column2.foreign_keys[0].column.table == srcTable and column1.foreign_keys[0].column.table == relatedTable:
                foundTable = table
                (column1,column2)=(column2,column1)
                break;
        if foundTable is None:
            return
        #clear it out
        foundTable.delete(whereclause=column1==srcID).execute()
        
        #add the new values
        for value in values:
            foundTable.insert(values={column1:srcID, column2:value}).execute()
        
        #this operation was successful
        return True
        
    def getAssociatedManyToManyTables(self, tableName):
        tables =self.getAssociationTables(tableName)
        srcTable = self.getTable(tableName)
        r = []
        for table in tables:
            for column in self.getTable(table).columns:
                key = column.foreign_keys[0]
                if key.column.table is not srcTable:
                    r.append(key.column.table.name)
                    continue
        return r
    
    def _findFirstColumn(self, tableName, possibleColumns):
        actualColumns = self.getColumns(tableName)
        viewColumn = None
        for columnName in possibleColumns:
            for actualName in actualColumns:
                if columnName in actualName:
                    viewColumn = actualName
                    break
            if viewColumn:
                break;
        if viewColumn is None:
            viewColumn = actualColumns[0]
        return viewColumn
    
    def isBinaryColumn(self, tableName, columnName):
        return columnName in self.getColumns(tableName) and isinstance(self.getColumn(tableName, columnName).type, Binary)
    
    def getViewColumnName(self, tableName, possibleColumns=['_name', 'name', 'description', 'title']):
        return self._findFirstColumn(tableName, possibleColumns)

    def getIDColumnName(self, tableName):
        possibleColumns = ['_id', 'id']
        return self._findFirstColumn(tableName, possibleColumns)

    def _select(self, tableName, pks, values, columnsLimit, resultLimit, resultOffset, whereclauseJoin='and'):
        order_by = pks
        table = self.getTable(tableName)
        whereclause = self._generateWhereclause(table, pks, values, whereclauseJoin)
        columnListing=[table]
        if columnsLimit is not None:
            columnListing = self._generateColumnListing(table, columnsLimit)
            order_by      = columnListing
        s = select(columnListing, whereclause).offset(resultOffset).limit(resultLimit).order_by(*list(table.c))
        return s.execute().fetchall()
        
    def isUnique(self, field, value):
        s = select([field,], whereclause=field==value).execute().fetchall()
        return len(s) == 0

    #crud below
    def selectOnPks(self, tableName, values={}, columnsLimit=None, resultLimit=None, resultOffset=None):
        pks = self.getPrimaryKeys(tableName)
        return self._select(tableName, pks, values, columnsLimit, resultLimit, resultOffset)

    def select(self, tableName, values={}, columnsLimit=None, resultLimit=None, resultOffset=None, whereclauseJoin='and'):
        pks = values.keys()
        return self._select(tableName, pks, values, columnsLimit, resultLimit, resultOffset, whereclauseJoin)
    
    def count(self, tableName, values=None):
        table = self.getTable(tableName)
        return table.select().alias('all_data').count().execute().fetchall()[0][0]
         
    def add(self, tableName=None, values={}, columnsLimit=None):
        for key, value in values.iteritems():
            if isinstance(value, FieldStorage):
                values[key] = value.value
                
        #remove the primary keys which could cause a conflict
        kw = self._removePrimaryKeysIfNotForeign(tableName, values)
        #kw=self._removePrimaryKeys(tableName, values)
        from sys import stderr
        values = self._removeNonLimitColumns(values, columnsLimit)
        table = self.getTable(tableName)
        table.insert(values=kw).execute()
        
    def delete(self, tableName, values={}):
        table = self.getTable(tableName)
        pks = self.getPrimaryKeys(tableName)
        whereclause = self._generateWhereclause(table, pks, values)
        return table.delete(whereclause).execute()
        
    def edit(self, tableName, values={}, columnsLimit=None):
        pks = self.getPrimaryKeys(tableName)
        table = self.getTable(tableName)
        values = self._removeNonLimitColumns(values, columnsLimit)
        whereclause = self._generateWhereclause(table, pks, values)
        #remove the primary keys which could cause a conflict
        kw = self._removePrimaryKeys(tableName, values)
        table = self.getTable(tableName)
        if len(kw)>0:
            table.update(values=kw, whereclause=whereclause).execute()
    def isNullableField(self,field):
        return field.nullable