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

import transaction as zope_transaction
from zope.interface import implements
from transaction.interfaces import ISavepointDataManager, IDataManagerSavepoint
from sqlalchemy.orm.session import SessionExtension
from sqlalchemy.engine.base import Engine

# The status of the session is stored on the connection info
STATUS_ACTIVE = 'active' # session joined to transaction, writes allowed.
STATUS_CHANGED = 'changed' # data has been written
STATUS_READONLY = 'readonly' # session joined to transaction, no writes allowed.
STATUS_INVALIDATED = STATUS_CHANGED # BBB

NO_SAVEPOINT_SUPPORT = set(['sqlite'])


_SESSION_STATE = {} # a mapping of id(session) -> status
# This is thread safe because you are using scoped sessions


#
# The two variants of the DataManager.
#

class SessionDataManager(object):
    """Integrate a top level sqlalchemy session transaction into a zope transaction
    
    One phase variant.
    """
    
    implements(ISavepointDataManager)

    def __init__(self, session, status):
        self.tx = session.transaction._iterate_parents()[-1]
        self.session = session
        _SESSION_STATE[id(session)] = status
        self.state = 'init'

    def abort(self, trans):
        if self.tx is not None: # this could happen after a tpc_abort
            try:
                del _SESSION_STATE[id(self.session)]
            except Exception, e:
                pass

            self.session.close()
            self.tx = self.session = None
            self.state = 'aborted'

    def tpc_begin(self, trans):
        self.session._autoflush()
    
    def commit(self, trans):
        status = _SESSION_STATE[id(self.session)]
        del _SESSION_STATE[id(self.session)]
        if status is not STATUS_INVALIDATED:
            self.session.close()
            self.tx = self.session = None
            self.state = 'no work'

    def tpc_vote(self, trans):
        # for a one phase data manager commit last in tpc_vote
        if self.tx is not None: # there may have been no work to do
            try:
                self.tx.commit()
                self.session.close()
                self.tx = self.session = None
                self.state = 'finished on vote'
            except Exception, e:
                pass
                
    def tpc_finish(self, trans):
        pass

    def tpc_abort(self, trans):
        #raise TypeError("Already committed")
        pass

    def sortKey(self):
        # Try to sort last, so that we vote last - we may commit in tpc_vote(),
        # which allows Zope to roll back its transaction if the RDBMS 
        # threw a conflict error.
        return "~sqlalchemy:%d" % id(self.tx)
    
    @property
    def savepoint(self):
        """Savepoints are only supported when all connections support subtransactions
        """
        if set(engine.url.drivername
            for engine in self.session.transaction._connections.keys()
            if isinstance(engine, Engine)
            ).intersection(NO_SAVEPOINT_SUPPORT):
            raise AttributeError('savepoint')
        return self._savepoint
    
    def _savepoint(self):
        return SessionSavepoint(self.session)


class TwoPhaseSessionDataManager(SessionDataManager):
    """Two phase variant.
    """
    def tpc_vote(self, trans):
        if self.tx is not None: # there may have been no work to do
            self.tx.prepare()
            self.state = 'voted'
                
    def tpc_finish(self, trans):
        if self.tx is not None:
            self.tx.commit()
            self.session.close()
            self.tx = self.session = None
            self.state = 'finished'

    def tpc_abort(self, trans):
        if self.tx is not None: # we may not have voted, and been aborted already
            self.tx.rollback()
            self.session.close()
            self.tx = self.session = None
            self.state = 'aborted commit'

    def sortKey(self):
        # Sort normally
        return "sqlalchemy.twophase:%d" % id(self.tx)


class SessionSavepoint:
    implements(IDataManagerSavepoint)

    def __init__(self, session):
        self.session = session
        self.transaction = session.begin_nested()
        session.flush() # do I want to do this? Probably.

    def rollback(self):
        # no need to check validity, sqlalchemy should raise an exception. I think.
        self.transaction.rollback()
        self.session.clear() # remove when Session.rollback does an attribute_manager.rollback


def join_transaction(session, initial_state=STATUS_ACTIVE):
    """Join a session to a transaction using the appropriate datamanager.
       
    It is safe to call this multiple times, if the session is already joined
    then it just returns.
       
    `initial_state` is either STATUS_ACTIVE, STATUS_INVALIDATED or STATUS_READONLY
    
    If using the default initial status of STATUS_ACTIVE, you must ensure that
    dirty_session(session) is called when data is written to the database.
    
    The DirtyAfterFlush SessionExtension can be used to ensure that this is
    called automatically after session write operations.
    """
    if _SESSION_STATE.get(id(session), None) is None:
        DataManager = session.twophase and TwoPhaseSessionDataManager or SessionDataManager
        zope_transaction.get().join(DataManager(session, initial_state))

def mark_changed(session):
    """Mark a session as needing to be committed
    """
    assert _SESSION_STATE[id(session)] is not STATUS_READONLY
    _SESSION_STATE[id(session)] = STATUS_CHANGED


class ZopeTransactionExtension(SessionExtension):
    """Record that a flush has occurred on a session's connection. This allows
    the DataManager to rollback rather than commit on read only transactions.
    """
    
    def __init__(self, initial_state=STATUS_ACTIVE):
        if initial_state=='invalidated': initial_state = STATUS_CHANGED #BBB
        SessionExtension.__init__(self)
        self.initial_state = initial_state
    
    def after_begin(self, session, transaction, connection):
        join_transaction(session, self.initial_state)
    
    def after_attach(self, session, instance):
        join_transaction(session, self.initial_state)
    
    def after_flush(self, session, flush_context):
        mark_changed(session)
    
    def before_commit(self, session):
        #assert zope_transaction.get().status == 'Committing', "Transaction must be committed by zope"
        pass
