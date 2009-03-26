##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

# Much inspiration from z3c.sqlalchemy/trunk/src/z3c/sqlalchemy/tests/testSQLAlchemy.py
#
# You may want to run the tests with your database. To do so set the environment variable
# TEST_DSN to the connection url. e.g.:
# export TEST_DSN=postgres://plone:plone@localhost/test
# export TEST_DSN=mssql://plone:plone@/test?dsn=mydsn
#
# To test in twophase commit mode export TEST_TWOPHASE=True 
#
# NOTE: The sqlite that ships with Mac OS X 10.4 is buggy. Install a newer version (3.5.6)
#       and rebuild pysqlite2 against it.


import os
import unittest
import transaction
import threading
import sqlalchemy as sa
from sqlalchemy import orm, sql
from zope.sqlalchemy import datamanager as tx

TEST_TWOPHASE = bool(os.environ.get('TEST_TWOPHASE'))
TEST_DSN = os.environ.get('TEST_DSN', 'sqlite:///:memory:')

SA_0_4 = sa.__version__.split('.')[:2] == ['0', '4']
SA_0_5 = not SA_0_4


class SimpleModel(object):
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)
    def asDict(self):
        return dict((k, v) for k, v in self.__dict__.items() if not k.startswith('_'))

class User(SimpleModel): pass
class Skill(SimpleModel): pass


engine = sa.create_engine(TEST_DSN)
engine2 = sa.create_engine(TEST_DSN)

if SA_0_4:
    Session = orm.scoped_session(orm.sessionmaker(
        bind=engine,
        extension=tx.ZopeTransactionExtension(),
        transactional=True,
        autoflush=True,
        twophase=TEST_TWOPHASE,
        ))
    UnboundSession = orm.scoped_session(orm.sessionmaker(
        extension=tx.ZopeTransactionExtension(),
        transactional=True,
        autoflush=True,
        twophase=TEST_TWOPHASE,
        ))

if SA_0_5:
    Session = orm.scoped_session(orm.sessionmaker(
        bind=engine,
        extension=tx.ZopeTransactionExtension(),
        twophase=TEST_TWOPHASE,
        ))
    UnboundSession = orm.scoped_session(orm.sessionmaker(
        extension=tx.ZopeTransactionExtension(),
        twophase=TEST_TWOPHASE,
        ))

metadata = sa.MetaData() # best to use unbound metadata

test_users = sa.Table('test_users', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('firstname', sa.VARCHAR(255)), # mssql cannot do equality on a text type
    sa.Column('lastname', sa.VARCHAR(255)),
    )    
test_skills = sa.Table('test_skills', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('user_id', sa.Integer),
    sa.Column('name', sa.VARCHAR(255)),
    sa.ForeignKeyConstraint(('user_id',), ('test_users.id',)),
    )

orm.mapper(User, test_users,
    properties = {
        'skills': orm.relation(Skill,
            primaryjoin=test_users.columns['id']==test_skills.columns['user_id']),
    })
orm.mapper(Skill, test_skills)

bound_metadata1 = sa.MetaData(engine)
bound_metadata2 = sa.MetaData(engine2)

test_one = sa.Table('test_one', bound_metadata1, sa.Column('id', sa.Integer, primary_key=True))
test_two = sa.Table('test_two', bound_metadata2, sa.Column('id', sa.Integer, primary_key=True))

class TestOne(SimpleModel): pass
class TestTwo(SimpleModel): pass

orm.mapper(TestOne, test_one)
orm.mapper(TestTwo, test_two)


class DummyException(Exception):
    pass
 
class DummyTargetRaised(DummyException):
    pass  

class DummyTargetResult(DummyException):
    pass

class DummyDataManager(object):
    def __init__(self, key, target=None, args=(), kwargs={}):
        self.key = key
        self.target = target
        self.args = args
        self.kwargs = kwargs
    
    def abort(self, trans):
        pass

    def tpc_begin(self, trans):
        pass
    
    def commit(self, trans):
        pass

    def tpc_vote(self, trans):
        if self.target is not None:
            try:
                result = self.target(*self.args, **self.kwargs)
            except Exception, e:
                raise DummyTargetRaised(e)
            raise DummyTargetResult(result)
        else:
            raise DummyException('DummyDataManager cannot commit')

    def tpc_finish(self, trans):
        pass

    def tpc_abort(self, trans):
        pass
    
    def sortKey(self):
        return self.key


class ZopeSQLAlchemyTests(unittest.TestCase):
        
    def setUp(self):
        metadata.drop_all(engine)
        metadata.create_all(engine)
    
    def tearDown(self):
        transaction.abort()
        metadata.drop_all(engine)

    def testSimplePopulation(self):
        session = Session()
        query = session.query(User)
        rows = query.all()
        self.assertEqual(len(rows), 0)
               
        session.save(User(id=1, firstname='udo', lastname='juergens'))
        session.save(User(id=2, firstname='heino', lastname='n/a'))
        session.flush()
        
        rows = query.order_by(User.id).all()
        self.assertEqual(len(rows), 2)
        row1 = rows[0]
        d = row1.asDict()
        self.assertEqual(d, {'firstname' : 'udo', 'lastname' : 'juergens', 'id' : 1})
        
        # bypass the session machinary
        stmt = sql.select(test_users.columns).order_by('id')
        conn = session.connection()
        results = conn.execute(stmt)
        self.assertEqual(results.fetchall(), [(1, u'udo', u'juergens'), (2, u'heino', u'n/a')])
        
    def testRelations(self):
        session = Session()
        session.save(User(id=1,firstname='foo', lastname='bar'))

        user = session.query(User).filter_by(firstname='foo')[0]
        user.skills.append(Skill(id=1, name='Zope'))
        session.flush()
    
    def testTransactionJoining(self):
        transaction.abort() # clean slate
        t = transaction.get()
        self.failIf([r for r in t._resources if isinstance(r, tx.SessionDataManager)],
             "Joined transaction too early")
        session = Session()
        session.save(User(id=1, firstname='udo', lastname='juergens'))
        t = transaction.get()
        # Expect this to fail with SQLAlchemy 0.4
        self.failUnless([r for r in t._resources if isinstance(r, tx.SessionDataManager)],
             "Not joined transaction")
        transaction.abort()
        conn = Session().connection()
        self.failUnless([r for r in t._resources if isinstance(r, tx.SessionDataManager)],
             "Not joined transaction")
    
    def testSavepoint(self):
        use_savepoint = not engine.url.drivername in tx.NO_SAVEPOINT_SUPPORT
        t = transaction.get()
        session = Session()
        query = session.query(User)
        self.failIf(query.all(), "Users table should be empty")
        
        s0 = t.savepoint(optimistic=True) # this should always work
        
        if not use_savepoint:
            self.assertRaises(TypeError, t.savepoint)
            return # sqlite databases do not support savepoints
        
        s1 = t.savepoint()
        session.save(User(id=1, firstname='udo', lastname='juergens'))
        session.flush()
        self.failUnless(len(query.all())==1, "Users table should have one row")
        
        s2 = t.savepoint()
        session.save(User(id=2, firstname='heino', lastname='n/a'))
        session.flush()
        self.failUnless(len(query.all())==2, "Users table should have two rows")
        
        s2.rollback()
        self.failUnless(len(query.all())==1, "Users table should have one row")
        
        s1.rollback()
        self.failIf(query.all(), "Users table should be empty")
    
    def testCommit(self):
        session = Session()
        
        use_savepoint = not engine.url.drivername in tx.NO_SAVEPOINT_SUPPORT
        query = session.query(User)
        rows = query.all()
        self.assertEqual(len(rows), 0)
        
        transaction.commit() # test a none modifying transaction works
        
        session = Session()
        query = session.query(User)

        session.save(User(id=1, firstname='udo', lastname='juergens'))
        session.save(User(id=2, firstname='heino', lastname='n/a'))
        session.flush()

        rows = query.order_by(User.id).all()
        self.assertEqual(len(rows), 2)
        
        transaction.abort() # test that the abort really aborts
        session = Session()
        query = session.query(User)
        rows = query.order_by(User.id).all()
        self.assertEqual(len(rows), 0)
        
        session.save(User(id=1, firstname='udo', lastname='juergens'))
        session.save(User(id=2, firstname='heino', lastname='n/a'))
        session.flush()
        rows = query.order_by(User.id).all()
        row1 = rows[0]
        d = row1.asDict()
        self.assertEqual(d, {'firstname' : 'udo', 'lastname' : 'juergens', 'id' : 1})
        
        transaction.commit()

        rows = query.order_by(User.id).all()
        self.assertEqual(len(rows), 2)
        row1 = rows[0]
        d = row1.asDict()
        self.assertEqual(d, {'firstname' : 'udo', 'lastname' : 'juergens', 'id' : 1})

        # bypass the session (and transaction) machinary
        results = engine.connect().execute(test_users.select())
        self.assertEqual(len(results.fetchall()), 2)

    def testCommitWithSavepoint(self):
        if engine.url.drivername in tx.NO_SAVEPOINT_SUPPORT:
            return
        session = Session()
        session.save(User(id=1, firstname='udo', lastname='juergens'))
        session.save(User(id=2, firstname='heino', lastname='n/a'))
        session.flush()
        transaction.commit()
        
        session = Session()
        query = session.query(User)
        # lets just test that savepoints don't affect commits
        t = transaction.get()
        rows = query.order_by(User.id).all()

        s1 = t.savepoint()
        session.delete(rows[1])
        session.flush()
        transaction.commit()

        # bypass the session machinary
        results = engine.connect().execute(test_users.select())
        self.assertEqual(len(results.fetchall()), 1)

    def testTwoPhase(self):
        session = Session()
        if not session.twophase:
            return
        session.save(User(id=1, firstname='udo', lastname='juergens'))
        session.save(User(id=2, firstname='heino', lastname='n/a'))
        session.flush()
        transaction.commit()
        
        # Test that we clean up after a tpc_abort
        t = transaction.get()
        
        def target():
            return engine.connect().recover_twophase()
        
        dummy = DummyDataManager(key='~~~dummy.last', target=target)
        t.join(dummy)
        session = Session()
        query = session.query(User)
        rows = query.all()
        session.delete(rows[0])
        session.flush()
        result = None
        try:
            t.commit()
        except DummyTargetResult, e:
            result = e.args[0]
        except DummyTargetRaised, e:
            raise e.args[0]
        
        self.assertEqual(len(result), 1, "Should have been one prepared transaction when dummy aborted")
        
        transaction.begin()
    
        self.assertEqual(len(engine.connect().recover_twophase()), 0, "Test no outstanding prepared transactions")

    
    def testThread(self):
        transaction.abort()
        global thread_error
        thread_error = None
        def target():
            try:
                session = Session()
                metadata.drop_all(engine)
                metadata.create_all(engine)
            
                query = session.query(User)
                rows = query.all()
                self.assertEqual(len(rows), 0)

                session.save(User(id=1, firstname='udo', lastname='juergens'))
                session.save(User(id=2, firstname='heino', lastname='n/a'))
                session.flush()

                rows = query.order_by(User.id).all()
                self.assertEqual(len(rows), 2)
                row1 = rows[0]
                d = row1.asDict()
                self.assertEqual(d, {'firstname' : 'udo', 'lastname' : 'juergens', 'id' : 1})
            except Exception, err:
                global thread_error
                thread_error = err
            transaction.abort()
        
        thread = threading.Thread(target=target)
        thread.start()
        thread.join()
        if thread_error is not None:
            raise thread_error # reraise in current thread


class MultipleEngineTests(unittest.TestCase):
        
    def setUp(self):
        bound_metadata1.drop_all()
        bound_metadata1.create_all()
        bound_metadata2.drop_all()
        bound_metadata2.create_all()
    
    def tearDown(self):
        transaction.abort()
        bound_metadata1.drop_all()
        bound_metadata2.drop_all()

    def testTwoEngines(self):
        session = UnboundSession()
        session.save(TestOne(id=1))
        session.save(TestTwo(id=2))
        session.flush()
        transaction.commit()
        session = UnboundSession()
        rows = session.query(TestOne).all()
        self.assertEqual(len(rows), 1)
        rows = session.query(TestTwo).all()
        self.assertEqual(len(rows), 1)

def tearDownReadMe(test):
    Base = test.globs['Base']
    engine = test.globs['engine']
    Base.metadata.drop_all(engine)

def test_suite():
    from unittest import TestSuite, makeSuite
    import doctest
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    suite = TestSuite()
    for cls in (ZopeSQLAlchemyTests, MultipleEngineTests):
        suite.addTest(makeSuite(cls))
    suite.addTest(doctest.DocFileSuite('README.txt', optionflags=optionflags, tearDown=tearDownReadMe,
        globs={'TEST_DSN': TEST_DSN, 'TEST_TWOPHASE': TEST_TWOPHASE, 'SA_0_4': SA_0_4, 'SA_0_5': SA_0_5}))
    return suite
