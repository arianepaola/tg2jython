import os
from sqlalchemy import *
from sqlalchemy.orm import *
from dbsprockets.test.model import *
from cStringIO import StringIO
from cgi import FieldStorage
sortedTableList = ['group_permission', 'permission', 'test_table', 'tg_group', 
                   'tg_user', 'town_table', 'user_group', 'user_reference','visit', 'visit_identity', ]
import pkg_resources; 
pkg_resources.require('mysql-python')

session = None
engine = None
def setupDatabase():
    global session, engine
    engine = create_engine(os.environ.get('DBURL', 'sqlite://'))
    metadata.bind = engine
    metadata.drop_all()
    metadata.create_all()

    Session = sessionmaker(bind=engine, autoflush=True, transactional=True)
    session = Session()
    
    user = User()
    user.user_name = u'asdf'
    user.email = u"asdf@asdf.com"
    user.password = u"asdf"
    
    arvada = Town(name=u'Arvada')
    session.save(arvada)
    session.save(Town(name=u'Denver'))
    session.save(Town(name=u'Golden'))
    session.save(Town(name=u'Boulder'))
    session.commit()

    test_table.insert(values=dict(BLOB=FieldStorage('asdf', StringIO()).value)).execute()
    user_reference_table.insert(values=dict(user_id=1)).execute()
    user.town = arvada.town_id
    session.save(user)
    
    for i in range (50):
        group = Group(group_name=unicode(i))
        session.save(group)
    
    user.groups.append(group)

    session.save(user)
    session.flush()
    session.commit()

def teardownDatabase():
    metadata.drop_all()

def _reassign_from_metadata():
    global visits_table, visit_identity_table, groups_table, town_table
    global users_table, permissions_table, user_group_table
    global group_permission_table, test_table

    visits_table = metadata.tables['visit']
    visit_identity_table = metadata.tables['visit_identity']
    groups_table = metadata.tables['tg_group']
    town_table = metadata.tables['town_table']
    users_table = metadata.tables['tg_user']
    permissions_table = metadata.tables['permission']
    user_group_table = metadata.tables['user_group']
    group_permission_table = metadata.tables['group_permission']
    test_table = metadata.tables['test_table']
    
def setupReflection():
    #if os.environ.get('AUTOLOAD', False):
    metadata.clear()
    metadata.reflect()
    _reassign_from_metadata()

    clear_mappers()
    tables = metadata.tables
    mapper(Town, tables['town_table'])
    mapper(Example, tables['test_table'])
    mapper(Visit, tables['visit'])
    mapper(VisitIdentity, tables['visit_identity'],
           properties=dict(users=relation(User, backref='visit_identity')))
    mapper(User, tables['tg_user'])
    mapper(Group, tables['tg_group'],
           properties=dict(users=relation(User,
                                          secondary=tables['user_group'],
                                          backref='groups')))
    mapper(Permission, tables['permission'],
           properties=dict(groups=relation(Group,
                                           secondary=tables['group_permission'],
                                           backref='permissions')))

    
if __name__ == '__main__':
    setupDatabase()
