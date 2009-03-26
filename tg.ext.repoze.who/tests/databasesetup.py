import os
from sqlalchemy import *
from sqlalchemy.orm import *
from model import *
from cStringIO import StringIO
from cgi import FieldStorage
sortedTableList = ['group_permission', 'permission', 'test_table', 'tg_group', 
                   'tg_user', 'town_table', 'user_group', 'visit', 'visit_identity', ]

session = None
Session = None
engine = None

import sha
def setup_database():
    global session, Session
    global engine
    engine = create_engine(os.environ.get('DBURL', 'sqlite://'))
    metadata.bind = engine
    metadata.drop_all()
    metadata.create_all()

    Session = sessionmaker(bind=engine, autoflush=True, transactional=True)
    session = Session()
    
    user = User()
    user.user_name = u'asdf'
    user.email = u"asdf@asdf.com"
    user.password = u'asdf'

    admin = Group(u'admin')
    session.save(admin)
    
    read = Permission()
    read.permission_name = u'read'
    session.save(read)
    
    write = Permission()
    write.permission_name = u'write'
    session.save(write)
    
    reader = Group(u'reader')
    reader.permissions.append(read)
    session.save(reader)
    
    writer = Group(u'writer')
    writer.permissions = [read, write]
    session.save(writer)
    
    user.groups.append(admin)

    session.save(user)
    
    user = User()
    user.user_name = u'robert'
    user.email = u"rob@asdf.com"
    user.password = u'robert'
    user.groups.append(reader)
    session.save(user)
    
    user = User()
    user.user_name = u'wendy'
    user.email = u"wendy@asdf.com"
    user.password = u'wendy'
    user.groups.append(writer)
    user.groups.append(reader)
    session.save(user)
    
    session.commit()

def teardownDatabase():
    pass
#    metadata.drop_all()

