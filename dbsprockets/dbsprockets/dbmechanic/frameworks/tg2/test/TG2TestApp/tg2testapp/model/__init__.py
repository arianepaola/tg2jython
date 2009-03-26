from pylons import config
from datetime import datetime
from sqlalchemy import *#Column, MetaData, Table, types
from sqlalchemy.orm import mapper, relation
from sqlalchemy.orm import scoped_session, sessionmaker

# Global session manager.  Session() returns the session object
# appropriate for the current web request.
DBSession = scoped_session(sessionmaker(autoflush=True, transactional=True))

# Global metadata. If you have multiple databases with overlapping table
# names, you'll need a metadata for each database.
metadata = MetaData()

def init_model(d):
    pass

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
    Column('user_id', Integer, ForeignKey('tg_user.user_id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('tg_group.group_id'), primary_key=True)
)

group_permission_table = Table('group_permission', metadata,
    Column('group_id', Integer, ForeignKey('tg_group.group_id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permission.permission_id'), primary_key=True)
)

test_table = Table('test_table', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('created', DateTime, default=datetime.now),
                   Column('BLOB',         BLOB          ),
                   Column('BOOLEAN_',      BOOLEAN       ),
                   Column('Binary',       Binary        ),
                   Column('Boolean',      Boolean       ),
                   Column('CHAR',         CHAR(200)     ),
                   Column('CLOB',         CLOB(200)     ),
                   Column('DATE_',         DATE          ),
                   Column('DATETIME_',     DATETIME      ),
                   Column('DECIMAL',      DECIMAL       ),
                   Column('Date',         Date          ),
                   Column('DateTime',     DateTime      ),
                   Column('FLOAT_',        FLOAT         ),
                   Column('Float',        Float         ),
                   Column('INT',          INT           ),
                   Column('Integer',      Integer       ),
        #           Column('NCHAR',        NCHAR         ),
                   Column('Numeric',      Numeric       ),
                   Column('PickleType',   PickleType    ),
                   Column('SMALLINT',     SMALLINT      ),
                   Column('SmallInteger', SmallInteger  ),
                   Column('String',       String        ),
                   Column('TEXT',         TEXT          ),
                   Column('TIME_',         TIME          ),
                   Column('Time',         Time          ),
                   Column('TIMESTAMP',    TIMESTAMP     ),
                   Column('Unicode',      Unicode       ),
                   Column('VARCHAR',      VARCHAR(200)  ),
                   )

class Example(object):
    pass

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
