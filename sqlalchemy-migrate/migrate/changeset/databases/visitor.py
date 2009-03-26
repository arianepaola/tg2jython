import sqlalchemy as sa
from migrate.changeset.databases import sqlite,postgres,mysql,oracle
from migrate.changeset import ansisql

# Map SA dialects to the corresponding Migrate extensions
dialects = {
    sa.engine.default.DefaultDialect : ansisql.ANSIDialect,
    sa.databases.sqlite.SQLiteDialect : sqlite.SQLiteDialect,
    sa.databases.postgres.PGDialect : postgres.PGDialect,
    sa.databases.mysql.MySQLDialect : mysql.MySQLDialect,
    sa.databases.oracle.OracleDialect : oracle.OracleDialect,
}

def get_engine_visitor(engine,name):
    return get_dialect_visitor(engine.dialect,name)

def get_dialect_visitor(sa_dialect,name):
    sa_dialect_cls = sa_dialect.__class__
    migrate_dialect_cls = dialects[sa_dialect_cls]
    return migrate_dialect_cls.visitor(name)
