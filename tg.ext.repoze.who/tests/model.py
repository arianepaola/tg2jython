from datetime import datetime
from sqlalchemy import *
from sqlalchemy.orm import *
metadata = MetaData()
from sqlalchemy.orm import scoped_session, sessionmaker

# Global session manager.  Session() returns the session object
# appropriate for the current web request.
Session = scoped_session(sessionmaker(autoflush=True, transactional=True))

# The identity schema.
visits_table = Table('visit', metadata,
    Column('visit_key', String(40), primary_key=True),
    Column('created', DateTime, nullable=False, default=datetime.now),
    Column('expiry', DateTime),
    mysql_engine='innodb',

)

visit_identity_table = Table('visit_identity', metadata,
    Column('visit_key', String(40), primary_key=True),
    Column('user_id', Integer, ForeignKey('tg_user.user_id'), index=True),
    mysql_engine='innodb',

)

groups_table = Table('tg_group', metadata,
    Column('group_id', Integer, primary_key=True),
    Column('group_name', Unicode(16), unique=True),
    Column('display_name', Unicode(255)),
    Column('created', DateTime, default=datetime.now),
    mysql_engine='innodb',
)

users_table = Table('tg_user', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('user_name', String(16), unique=True),
    Column('email_address', Unicode(255), unique=True),
    Column('display_name', Unicode(255)),
    Column('password', Unicode(40)),
    Column('created', DateTime, default=datetime.now),
    mysql_engine='innodb',

)

permissions_table = Table('permission', metadata,
    Column('permission_id', Integer, primary_key=True),
    Column('permission_name', Unicode(16), unique=True),
    Column('description', Unicode(255)),
    mysql_engine='innodb',

)

user_group_table = Table('user_group', metadata,
    Column('user_id', Integer, ForeignKey('tg_user.user_id')),
    Column('group_id', Integer, ForeignKey('tg_group.group_id')),
    mysql_engine='innodb',
)

group_permission_table = Table('group_permission', metadata,
    Column('group_id', Integer, ForeignKey('tg_group.group_id')),
    Column('permission_id', Integer, ForeignKey('permission.permission_id')),
    mysql_engine='innodb',
)

class Visit(object):
    def lookup_visit(cls, visit_key):
        return Visit.get(visit_key)
    lookup_visit = classmethod(lookup_visit)

class VisitIdentity(object):
    pass

class Group(object):
    """
    An ultra-simple group definition.
    """
    def __init__(self, group_name, display_name=u''):
        self.group_name = group_name
        self.display_name = display_name

class User(object):
    """
    Reasonably basic User definition. Probably would want additional
    attributes.
    """
    #def __init__(self, user_name=None,
    #             password=None,
    #             email=None):
    #    self.user_name = user_name
    #    self.password = password
    #    self.email = email
    @property
    def permissions(self):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms
    
    def validate_password(self, password):
        """Check the password against existing credentials.
        """
        
        return self.password == self.password


class Permission(object):
    pass

mapper( Visit, visits_table)
mapper( VisitIdentity, visit_identity_table,
          properties=dict(users=relation(User, backref='visit_identity')))
mapper( User, users_table)
mapper( Group, groups_table,
          properties=dict(users=relation(User,secondary=user_group_table, backref='groups')))
mapper( Permission, permissions_table,
          properties=dict(groups=relation(Group,secondary=group_permission_table, backref='permissions')))
