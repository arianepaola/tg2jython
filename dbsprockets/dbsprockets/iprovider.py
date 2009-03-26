"""
iprovider Module

this contains the class which allows dbsprockets to interface with any database.

Classes:
Name             Description
IProvider        provider interface

Exceptions:
None

Functions:
None


Copywrite (c) 2007 Christopher Perkins
Original Version by Christopher Perkins 2007
Released under MIT license.
"""

class IProvider:
    #table information stuff
    def getTables(self):
        """()->[list of tablesNames] 
        get a list of tables from the database"""
        raise NotImplementedError
    def getTable(self, name):
        """(name) -> sqlalchemy.schema.Table
        get the table definition with the given table name
        """
        raise NotImplementedError
    def getColumns(self, tableName):
        """(name) -> [list of columnNames]
        get the column names given the table name
        """
        raise NotImplementedError
    def getColumn(self, tableName, name):
        """(tableName, name) -> sqlalchemy.schema.Column
        get the column definition givcen the tablename and column name.
        """
        raise NotImplementedError
    def getPrimaryKeys(self, tableName):
        raise NotImplementedError

    #crud stuff
    def select(self, tableName, **kw):
        raise NotImplementedError
    def add(self, tableName=None, **kw):
        raise NotImplementedError
    def edit(self, tableName=None, **kw):
        raise NotImplementedError
    def isNullableField(self,field):
        raise NotImplementedError