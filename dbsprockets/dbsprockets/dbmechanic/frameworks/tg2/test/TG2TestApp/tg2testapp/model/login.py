from sqlalchemy import Column, Table, types
from sqlalchemy.orm import mapper, relation
from sqlalchemy.orm import scoped_session, sessionmaker
from tgpybrewerycontroller.model.base import metadata

# The identity schema.
visits_table = Table('visit', metadata,
    Column('visit_key', String(40), primary_key=True),
    Column('created', DateTime, nullable=False, default=datetime.now),
    Column('expiry', DateTime)
)

visit_identity_table = Table('visit_identity', metadata,
    Column('visit_key', String(40), primary_key=True),
    Column('user_id', Integer, ForeignKey('tg_user.user_id'), index=True)
)

groups_table = Table('tg_group', metadata,
    Column('group_id', Integer, primary_key=True),
    Column('group_name', Unicode(16), unique=True),
    Column('display_name', Unicode(255)),
    Column('created', DateTime, default=datetime.now)
)

town_table = Table('town_table', metadata,
    Column('town_id', Integer, primary_key=True),
    Column('name', Unicode(255)))

users_table = Table('tg_user', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('user_name', Unicode(16), unique=True),
    Column('email_address', Unicode(255), unique=True),
    Column('display_name', Unicode(255)),
    Column('password', Unicode(40)),
    Column('town', Integer, ForeignKey('town_table.town_id')),
    Column('created', DateTime, default=datetime.now)
)
permissions_table = Table('permission', metadata,
    Column('permission_id', Integer, primary_key=True),
    Column('permission_name', Unicode(16), unique=True),
    Column('description', Unicode(255))
)

user_group_table = Table('user_group', metadata,
    Column('user_id', Integer, ForeignKey('tg_user.user_id')),
    Column('group_id', Integer, ForeignKey('tg_group.group_id'))
)

group_permission_table = Table('group_permission', metadata,
    Column('group_id', Integer, ForeignKey('tg_group.group_id')),
    Column('permission_id', Integer, ForeignKey('permission.permission_id'))
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
    pass

class User(object):
    """
    Reasonably basic User definition. Probably would want additional
    attributes.
    """
    def __init__(self, user_name=None,
                 password=None,
                 email=None):
        self.user_name = user_name
        self.password = password
        self.email = email

    def permissions(self):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms
    permissions = property(permissions)

class Permission(object):
    pass

mapper( Example, test_table)
mapper( Visit, visits_table)
mapper( VisitIdentity, visit_identity_table,
          properties=dict(users=relation(User, backref='visit_identity')))
mapper( User, users_table)
mapper( Group, groups_table,
          properties=dict(users=relation(User,secondary=user_group_table, backref='groups')))
mapper( Permission, permissions_table,
          properties=dict(groups=relation(Group,secondary=group_permission_table, backref='permissions')))
