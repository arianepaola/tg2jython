"""TestCase and TestSuite artifacts and testing decorators."""

# monkeypatches unittest.TestLoader.suiteClass at import time

import itertools
import operator
import re
import sys
import types
from testlib import sa_unittest as unittest
import warnings
from cStringIO import StringIO

import testlib.config as config
from testlib.compat import _function_named

# Delayed imports
MetaData = None
Session = None
clear_mappers = None
sa_exc = None
schema = None
sqltypes = None
util = None


_ops = { '<': operator.lt,
         '>': operator.gt,
         '==': operator.eq,
         '!=': operator.ne,
         '<=': operator.le,
         '>=': operator.ge,
         'in': operator.contains,
         'between': lambda val, pair: val >= pair[0] and val <= pair[1],
         }

# sugar ('testing.db'); set here by config() at runtime
db = None

# more sugar, installed by __init__
requires = None

def fails_if(callable_):
    """Mark a test as expected to fail if callable_ returns True.

    If the callable returns false, the test is run and reported as normal.
    However if the callable returns true, the test is expected to fail and the
    unit test logic is inverted: if the test fails, a success is reported.  If
    the test succeeds, a failure is reported.
    """

    docstring = getattr(callable_, '__doc__', None) or callable_.__name__
    description = docstring.split('\n')[0]

    def decorate(fn):
        fn_name = fn.__name__
        def maybe(*args, **kw):
            if not callable_():
                return fn(*args, **kw)
            else:
                try:
                    fn(*args, **kw)
                except Exception, ex:
                    print ("'%s' failed as expected (condition: %s): %s " % (
                        fn_name, description, str(ex)))
                    return True
                else:
                    raise AssertionError(
                        "Unexpected success for '%s' (condition: %s)" %
                        (fn_name, description))
        return _function_named(maybe, fn_name)
    return decorate


def future(fn):
    """Mark a test as expected to unconditionally fail.

    Takes no arguments, omit parens when using as a decorator.
    """

    fn_name = fn.__name__
    def decorated(*args, **kw):
        try:
            fn(*args, **kw)
        except Exception, ex:
            print ("Future test '%s' failed as expected: %s " % (
                fn_name, str(ex)))
            return True
        else:
            raise AssertionError(
                "Unexpected success for future test '%s'" % fn_name)
    return _function_named(decorated, fn_name)

def db_spec(*dbs):
    dialects = set([x for x in dbs if '+' not in x])
    drivers = set([x[1:] for x in dbs if x.startswith('+')])
    specs = set([tuple(x.split('+')) for x in dbs if '+' in x and x not in drivers])

    def check(engine):
        return engine.name in dialects or \
            engine.driver in drivers or \
            (engine.name, engine.driver) in specs
    
    return check
        

def fails_on(dbs, reason):
    """Mark a test as expected to fail on the specified database 
    implementation.

    Unlike ``crashes``, tests marked as ``fails_on`` will be run
    for the named databases.  The test is expected to fail and the unit test
    logic is inverted: if the test fails, a success is reported.  If the test
    succeeds, a failure is reported.
    """

    spec = db_spec(dbs)
    
    def decorate(fn):
        fn_name = fn.__name__
        def maybe(*args, **kw):
            if not spec(config.db):
                return fn(*args, **kw)
            else:
                try:
                    fn(*args, **kw)
                except Exception, ex:
                    print ("'%s' failed as expected on DB implementation "
                           "'%s+%s': %s" % (
                        fn_name, config.db.name, config.db.driver, reason))
                    return True
                else:
                    raise AssertionError(
                        "Unexpected success for '%s' on DB implementation '%s+%s'" %
                        (fn_name, config.db.name, config.db.driver))
        return _function_named(maybe, fn_name)
    return decorate

def fails_on_everything_except(*dbs):
    """Mark a test as expected to fail on most database implementations.

    Like ``fails_on``, except failure is the expected outcome on all
    databases except those listed.
    """

    spec = db_spec(*dbs)
    
    def decorate(fn):
        fn_name = fn.__name__
        def maybe(*args, **kw):
            if spec(config.db):
                return fn(*args, **kw)
            else:
                try:
                    fn(*args, **kw)
                except Exception, ex:
                    print ("'%s' failed as expected on DB implementation "
                           "'%s+%s': %s" % (
                        fn_name, config.db.name, config.db.driver, str(ex)))
                    return True
                else:
                    raise AssertionError(
                        "Unexpected success for '%s' on DB implementation '%s+%s'" %
                        (fn_name, config.db.name, config.db.driver))
        return _function_named(maybe, fn_name)
    return decorate

def crashes(db, reason):
    """Mark a test as unsupported by a database implementation.

    ``crashes`` tests will be skipped unconditionally.  Use for feature tests
    that cause deadlocks or other fatal problems.

    """
    carp = _should_carp_about_exclusion(reason)
    spec = db_spec(db)
    def decorate(fn):
        fn_name = fn.__name__
        def maybe(*args, **kw):
            if spec(config.db):
                msg = "'%s' unsupported on DB implementation '%s+%s': %s" % (
                    fn_name, config.db.name, config.db.driver, reason)
                print msg
                if carp:
                    print >> sys.stderr, msg
                return True
            else:
                return fn(*args, **kw)
        return _function_named(maybe, fn_name)
    return decorate

def _block_unconditionally(db, reason):
    """Mark a test as unsupported by a database implementation.

    Will never run the test against any version of the given database, ever,
    no matter what.  Use when your assumptions are infallible; past, present
    and future.

    """
    carp = _should_carp_about_exclusion(reason)
    spec = db_spec(db)
    def decorate(fn):
        fn_name = fn.__name__
        def maybe(*args, **kw):
            if spec(config.db):
                msg = "'%s' unsupported on DB implementation '%s+%s': %s" % (
                    fn_name, config.db.name, config.db.driver, reason)
                print msg
                if carp:
                    print >> sys.stderr, msg
                return True
            else:
                return fn(*args, **kw)
        return _function_named(maybe, fn_name)
    return decorate


def exclude(db, op, spec, reason):
    """Mark a test as unsupported by specific database server versions.

    Stackable, both with other excludes and other decorators. Examples::

      # Not supported by mydb versions less than 1, 0
      @exclude('mydb', '<', (1,0))
      # Other operators work too
      @exclude('bigdb', '==', (9,0,9))
      @exclude('yikesdb', 'in', ((0, 3, 'alpha2'), (0, 3, 'alpha3')))

    """
    carp = _should_carp_about_exclusion(reason)
    
    def decorate(fn):
        fn_name = fn.__name__
        def maybe(*args, **kw):
            if _is_excluded(db, op, spec):
                msg = "'%s' unsupported on DB %s version '%s': %s" % (
                    fn_name, config.db.name, _server_version(), reason)
                print msg
                if carp:
                    print >> sys.stderr, msg
                return True
            else:
                return fn(*args, **kw)
        return _function_named(maybe, fn_name)
    return decorate

def _should_carp_about_exclusion(reason):
    """Guard against forgotten exclusions."""
    assert reason
    for _ in ('todo', 'fixme', 'xxx'):
        if _ in reason.lower():
            return True
    else:
        if len(reason) < 4:
            return True

def _is_excluded(db, op, spec):
    """Return True if the configured db matches an exclusion specification.

    db:
      A dialect name
    op:
      An operator or stringified operator, such as '=='
    spec:
      A value that will be compared to the dialect's server_version_info
      using the supplied operator.

    Examples::
      # Not supported by mydb versions less than 1, 0
      _is_excluded('mydb', '<', (1,0))
      # Other operators work too
      _is_excluded('bigdb', '==', (9,0,9))
      _is_excluded('yikesdb', 'in', ((0, 3, 'alpha2'), (0, 3, 'alpha3')))
    """

    vendor_spec = db_spec(db)

    if not vendor_spec(config.db):
        return False

    version = _server_version()

    oper = hasattr(op, '__call__') and op or _ops[op]
    return oper(version, spec)

def _server_version(bind=None):
    """Return a server_version_info tuple."""

    if bind is None:
        bind = config.db
    return getattr(bind.dialect, 'server_version_info', ())

def skip_if(predicate, reason=None):
    """Skip a test if predicate is true."""
    reason = reason or predicate.__name__
    def decorate(fn):
        fn_name = fn.__name__
        def maybe(*args, **kw):
            if predicate():
                msg = "'%s' skipped on DB %s version '%s': %s" % (
                    fn_name, config.db.name, _server_version(), reason)
                print msg
                return True
            else:
                return fn(*args, **kw)
        return _function_named(maybe, fn_name)
    return decorate

def emits_warning(*messages):
    """Mark a test as emitting a warning.

    With no arguments, squelches all SAWarning failures.  Or pass one or more
    strings; these will be matched to the root of the warning description by
    warnings.filterwarnings().
    """

    # TODO: it would be nice to assert that a named warning was
    # emitted. should work with some monkeypatching of warnings,
    # and may work on non-CPython if they keep to the spirit of
    # warnings.showwarning's docstring.
    # - update: jython looks ok, it uses cpython's module
    def decorate(fn):
        def safe(*args, **kw):
            global sa_exc
            if sa_exc is None:
                import sqlalchemy.exc as sa_exc

            # todo: should probably be strict about this, too
            filters = [dict(action='ignore',
                            category=sa_exc.SAPendingDeprecationWarning)]
            if not messages:
                filters.append(dict(action='ignore',
                                     category=sa_exc.SAWarning))
            else:
                filters.extend(dict(action='ignore',
                                     message=message,
                                     category=sa_exc.SAWarning)
                                for message in messages)
            for f in filters:
                warnings.filterwarnings(**f)
            try:
                return fn(*args, **kw)
            finally:
                resetwarnings()
        return _function_named(safe, fn.__name__)
    return decorate

def emits_warning_on(db, *warnings):
    """Mark a test as emitting a warning on a specific dialect.

    With no arguments, squelches all SAWarning failures.  Or pass one or more
    strings; these will be matched to the root of the warning description by
    warnings.filterwarnings().
    """
    spec = db_spec(db)
    
    def decorate(fn):
        def maybe(*args, **kw):
            if isinstance(db, basestring):
                if not spec(config.db):
                    return fn(*args, **kw)
                else:
                    wrapped = emits_warning(*warnings)(fn)
                    return wrapped(*args, **kw)
            else:
                if not _is_excluded(*db):
                    return fn(*args, **kw)
                else:
                    wrapped = emits_warning(*warnings)(fn)
                    return wrapped(*args, **kw)
        return _function_named(maybe, fn.__name__)
    return decorate

def uses_deprecated(*messages):
    """Mark a test as immune from fatal deprecation warnings.

    With no arguments, squelches all SADeprecationWarning failures.
    Or pass one or more strings; these will be matched to the root
    of the warning description by warnings.filterwarnings().

    As a special case, you may pass a function name prefixed with //
    and it will be re-written as needed to match the standard warning
    verbiage emitted by the sqlalchemy.util.deprecated decorator.
    """

    def decorate(fn):
        def safe(*args, **kw):
            global sa_exc
            if sa_exc is None:
                import sqlalchemy.exc as sa_exc

            # todo: should probably be strict about this, too
            filters = [dict(action='ignore',
                            category=sa_exc.SAPendingDeprecationWarning)]
            if not messages:
                filters.append(dict(action='ignore',
                                    category=sa_exc.SADeprecationWarning))
            else:
                filters.extend(
                    [dict(action='ignore',
                          message=message,
                          category=sa_exc.SADeprecationWarning)
                     for message in
                     [ (m.startswith('//') and
                        ('Call to deprecated function ' + m[2:]) or m)
                       for m in messages] ])

            for f in filters:
                warnings.filterwarnings(**f)
            try:
                return fn(*args, **kw)
            finally:
                resetwarnings()
        return _function_named(safe, fn.__name__)
    return decorate

def resetwarnings():
    """Reset warning behavior to testing defaults."""

    global sa_exc
    if sa_exc is None:
        import sqlalchemy.exc as sa_exc

    warnings.filterwarnings('ignore',
                            category=sa_exc.SAPendingDeprecationWarning) 
    warnings.filterwarnings('error', category=sa_exc.SADeprecationWarning)
    warnings.filterwarnings('error', category=sa_exc.SAWarning)

#    warnings.simplefilter('error')

    if sys.version_info < (2, 4):
        warnings.filterwarnings('ignore', category=FutureWarning)


def against(*queries):
    """Boolean predicate, compares to testing database configuration.

    Given one or more dialect names, returns True if one is the configured
    database engine.

    Also supports comparison to database version when provided with one or
    more 3-tuples of dialect name, operator, and version specification::

      testing.against('mysql', 'postgres')
      testing.against(('mysql', '>=', (5, 0, 0))
    """

    for query in queries:
        if isinstance(query, basestring):
            if db_spec(query)(config.db):
                return True
        else:
            name, op, spec = query
            if not db_spec(name)(config.db):
                continue

            have = _server_version()

            oper = hasattr(op, '__call__') and op or _ops[op]
            if oper(have, spec):
                return True
    return False

def _chain_decorators_on(fn, *decorators):
    """Apply a series of decorators to fn, returning a decorated function."""
    for decorator in reversed(decorators):
        fn = decorator(fn)
    return fn

def rowset(results):
    """Converts the results of sql execution into a plain set of column tuples.

    Useful for asserting the results of an unordered query.
    """

    return set([tuple(row) for row in results])


def eq_(a, b, msg=None):
    """Assert a == b, with repr messaging on failure."""
    assert a == b, msg or "%r != %r" % (a, b)

def ne_(a, b, msg=None):
    """Assert a != b, with repr messaging on failure."""
    assert a != b, msg or "%r == %r" % (a, b)

def is_(a, b, msg=None):
    """Assert a is b, with repr messaging on failure."""
    assert a is b, msg or "%r is not %r" % (a, b)

def is_not_(a, b, msg=None):
    """Assert a is not b, with repr messaging on failure."""
    assert a is not b, msg or "%r is %r" % (a, b)

def startswith_(a, fragment, msg=None):
    """Assert a.startswith(fragment), with repr messaging on failure."""
    assert a.startswith(fragment), msg or "%r does not start with %r" % (
        a, fragment)


def fixture(table, columns, *rows):
    """Insert data into table after creation."""
    def onload(event, schema_item, connection):
        insert = table.insert()
        column_names = [col.key for col in columns]
        connection.execute(insert, [dict(zip(column_names, column_values))
                                    for column_values in rows])
    table.append_ddl_listener('after-create', onload)

def _import_by_name(name):
    submodule = name.split('.')[-1]
    return __import__(name, globals(), locals(), [submodule])

class CompositeModule(types.ModuleType):
    """Merged attribute access for multiple modules."""

    # break the habit
    __all__ = ()

    def __init__(self, name, *modules, **overrides):
        """Construct a new lazy composite of modules.

        Modules may be string names or module-like instances.  Individual
        attribute overrides may be specified as keyword arguments for
        convenience.

        The constructed module will resolve attribute access in reverse order:
        overrides, then each member of reversed(modules).  Modules specified
        by name will be loaded lazily when encountered in attribute
        resolution.

        """
        types.ModuleType.__init__(self, name)
        self.__modules = list(reversed(modules))
        for key, value in overrides.iteritems():
            setattr(self, key, value)

    def __getattr__(self, key):
        for idx, mod in enumerate(self.__modules):
            if isinstance(mod, basestring):
                self.__modules[idx] = mod = _import_by_name(mod)
            if hasattr(mod, key):
                return getattr(mod, key)
        raise AttributeError(key)


def resolve_artifact_names(fn):
    """Decorator, augment function globals with tables and classes.

    Swaps out the function's globals at execution time. The 'global' statement
    will not work as expected inside a decorated function.

    """
    # This could be automatically applied to framework and test_ methods in
    # the MappedTest-derived test suites but... *some* explicitness for this
    # magic is probably good.  Especially as 'global' won't work- these
    # rebound functions aren't regular Python..
    #
    # Also: it's lame that CPython accepts a dict-subclass for globals, but
    # only calls dict methods.  That would allow 'global' to pass through to
    # the func_globals.
    def resolved(*args, **kwargs):
        self = args[0]
        context = dict(fn.func_globals)
        for source in self._artifact_registries:
            context.update(getattr(self, source))
        # jython bug #1034
        rebound = types.FunctionType(
            fn.func_code, context, fn.func_name, fn.func_defaults,
            fn.func_closure)
        return rebound(*args, **kwargs)
    return _function_named(resolved, fn.func_name)

class adict(dict):
    """Dict keys available as attributes.  Shadows."""
    def __getattribute__(self, key):
        try:
            return self[key]
        except KeyError:
            return dict.__getattribute__(self, key)

    def get_all(self, *keys):
        return tuple([self[key] for key in keys])


class TestBase(unittest.TestCase):
    # A sequence of database names to always run, regardless of the
    # constraints below.
    __whitelist__ = ()

    # A sequence of requirement names matching testing.requires decorators
    __requires__ = ()

    # A sequence of dialect names to exclude from the test class.
    __unsupported_on__ = ()

    # If present, test class is only runnable for the *single* specified
    # dialect.  If you need multiple, use __unsupported_on__ and invert.
    __only_on__ = None

    # A sequence of no-arg callables. If any are True, the entire testcase is
    # skipped.
    __skip_if__ = None


    _artifact_registries = ()

    _sa_first_test = False
    _sa_last_test = False

    def __init__(self, *args, **params):
        unittest.TestCase.__init__(self, *args, **params)

    def setUpAll(self):
        pass

    def tearDownAll(self):
        pass

    def shortDescription(self):
        """overridden to not return docstrings"""
        return None

    def assertRaisesMessage(self, except_cls, msg, callable_, *args, **kwargs):
        try:
            callable_(*args, **kwargs)
            assert False, "Callable did not raise an exception"
        except except_cls, e:
            assert re.search(msg, str(e)), "%r !~ %s" % (msg, e)

    if not hasattr(unittest.TestCase, 'assertTrue'):
        assertTrue = unittest.TestCase.failUnless
    if not hasattr(unittest.TestCase, 'assertFalse'):
        assertFalse = unittest.TestCase.failIf

class AssertsCompiledSQL(object):
    def assert_compile(self, clause, result, params=None, checkparams=None, dialect=None):
        if dialect is None:
            dialect = getattr(self, '__dialect__', None)

        kw = {}
        if params is not None:
            kw['column_keys'] = params.keys()

        c = clause.compile(dialect=dialect, **kw)

        print "\nSQL String:\n" + str(c) + repr(getattr(c, 'params', {}))

        cc = re.sub(r'\n', '', str(c))

        self.assertEquals(cc, result, "%r != %r on dialect %r" % (cc, result, dialect))

        if checkparams is not None:
            self.assertEquals(c.construct_params(params), checkparams)

class ComparesTables(object):
    def assert_tables_equal(self, table, reflected_table):
        global sqltypes, schema
        if sqltypes is None:
            import sqlalchemy.types as sqltypes
        if schema is None:
            import sqlalchemy.schema as schema
        base_mro = sqltypes.TypeEngine.__mro__
        assert len(table.c) == len(reflected_table.c)
        for c, reflected_c in zip(table.c, reflected_table.c):
            self.assertEquals(c.name, reflected_c.name)
            assert reflected_c is reflected_table.c[c.name]
            self.assertEquals(c.primary_key, reflected_c.primary_key)
            self.assertEquals(c.nullable, reflected_c.nullable)
            assert len(
                set(type(reflected_c.type).__mro__).difference(base_mro).intersection(
                set(type(c.type).__mro__).difference(base_mro)
                )
            ) > 0, "Type '%s' doesn't correspond to type '%s'" % (reflected_c.type, c.type)

            if isinstance(c.type, sqltypes.String):
                self.assertEquals(c.type.length, reflected_c.type.length)

            self.assertEquals(set([f.column.name for f in c.foreign_keys]), set([f.column.name for f in reflected_c.foreign_keys]))
            if c.default:
                assert isinstance(reflected_c.server_default,
                                  schema.FetchedValue)
            elif against(('mysql', '<', (5, 0))):
                # ignore reflection of bogus db-generated DefaultClause()
                pass
            elif not c.primary_key or not against('postgres'):
                print repr(c)
                assert reflected_c.default is None, reflected_c.default

        assert len(table.primary_key) == len(reflected_table.primary_key)
        for c in table.primary_key:
            assert reflected_table.primary_key.columns[c.name]


class AssertsExecutionResults(object):
    def assert_result(self, result, class_, *objects):
        result = list(result)
        print repr(result)
        self.assert_list(result, class_, objects)

    def assert_list(self, result, class_, list):
        self.assert_(len(result) == len(list),
                     "result list is not the same size as test list, " +
                     "for class " + class_.__name__)
        for i in range(0, len(list)):
            self.assert_row(class_, result[i], list[i])

    def assert_row(self, class_, rowobj, desc):
        self.assert_(rowobj.__class__ is class_,
                     "item class is not " + repr(class_))
        for key, value in desc.iteritems():
            if isinstance(value, tuple):
                if isinstance(value[1], list):
                    self.assert_list(getattr(rowobj, key), value[0], value[1])
                else:
                    self.assert_row(value[0], getattr(rowobj, key), value[1])
            else:
                self.assert_(getattr(rowobj, key) == value,
                             "attribute %s value %s does not match %s" % (
                             key, getattr(rowobj, key), value))

    def assert_unordered_result(self, result, cls, *expected):
        """As assert_result, but the order of objects is not considered.

        The algorithm is very expensive but not a big deal for the small
        numbers of rows that the test suite manipulates.
        """

        global util
        if util is None:
            from sqlalchemy import util

        class frozendict(dict):
            def __hash__(self):
                return id(self)

        found = util.IdentitySet(result)
        expected = set([frozendict(e) for e in expected])

        for wrong in itertools.ifilterfalse(lambda o: type(o) == cls, found):
            self.fail('Unexpected type "%s", expected "%s"' % (
                type(wrong).__name__, cls.__name__))

        if len(found) != len(expected):
            self.fail('Unexpected object count "%s", expected "%s"' % (
                len(found), len(expected)))

        NOVALUE = object()
        def _compare_item(obj, spec):
            for key, value in spec.iteritems():
                if isinstance(value, tuple):
                    try:
                        self.assert_unordered_result(
                            getattr(obj, key), value[0], *value[1])
                    except AssertionError:
                        return False
                else:
                    if getattr(obj, key, NOVALUE) != value:
                        return False
            return True

        for expected_item in expected:
            for found_item in found:
                if _compare_item(found_item, expected_item):
                    found.remove(found_item)
                    break
            else:
                self.fail(
                    "Expected %s instance with attributes %s not found." % (
                    cls.__name__, repr(expected_item)))
        return True

    def assert_sql_execution(self, db, callable_, *rules):
        from testlib import assertsql
        assertsql.asserter.add_rules(rules)
        try:
            callable_()
            assertsql.asserter.statement_complete()
        finally:
            assertsql.asserter.clear_rules()
            
    def assert_sql(self, db, callable_, list_, with_sequences=None):
        from testlib import assertsql

        if with_sequences is not None and config.db.name in ('firebird', 'oracle', 'postgres'):
            rules = with_sequences
        else:
            rules = list_
        
        newrules = []
        for rule in rules:
            if isinstance(rule, dict):
                newrule = assertsql.AllOf(*[
                    assertsql.ExactSQL(k, v) for k, v in rule.iteritems()
                ])
            else:
                newrule = assertsql.ExactSQL(*rule)
            newrules.append(newrule)
            
        self.assert_sql_execution(db, callable_, *newrules)

    def assert_sql_count(self, db, callable_, count):
        from testlib import assertsql
        self.assert_sql_execution(db, callable_, assertsql.CountStatements(count))


_otest_metadata = None
class ORMTest(TestBase, AssertsExecutionResults):
    keep_mappers = False
    keep_data = False
    metadata = None

    def setUpAll(self):
        global MetaData, _otest_metadata

        if MetaData is None:
            from sqlalchemy import MetaData

        if self.metadata is None:
            _otest_metadata = MetaData(config.db)
        else:
            _otest_metadata = self.metadata
            if self.metadata.bind is None:
                _otest_metadata.bind = config.db
        self.define_tables(_otest_metadata)
        _otest_metadata.create_all()
        self.setup_mappers()
        self.insert_data()

    def define_tables(self, _otest_metadata):
        raise NotImplementedError()

    def setup_mappers(self):
        pass

    def insert_data(self):
        pass

    def get_metadata(self):
        return _otest_metadata

    def tearDownAll(self):
        global clear_mappers
        if clear_mappers is None:
            from sqlalchemy.orm import clear_mappers

        clear_mappers()
        _otest_metadata.drop_all()

    def tearDown(self):
        global Session
        if Session is None:
            from sqlalchemy.orm.session import Session
        Session.close_all()
        global clear_mappers
        if clear_mappers is None:
            from sqlalchemy.orm import clear_mappers

        if not self.keep_mappers:
            clear_mappers()
        if not self.keep_data:
            for t in reversed(_otest_metadata.sorted_tables):
                try:
                    t.delete().execute().close()
                except Exception, e:
                    print "EXCEPTION DELETING...", e


class TTestSuite(unittest.TestSuite):
    """A TestSuite with once per TestCase setUpAll() and tearDownAll()"""

    def __init__(self, tests=()):
        if len(tests) > 0 and isinstance(tests[0], TestBase):
            self._initTest = tests[0]
        else:
            self._initTest = None

        for t in tests:
            if isinstance(t, TestBase):
                t._sa_first_test = True
                break
        for t in reversed(tests):
            if isinstance(t, TestBase):
                t._sa_last_test = True
                break
        unittest.TestSuite.__init__(self, tests)

    def run(self, result):
        init = getattr(self, '_initTest', None)
        if init is not None:
            if (hasattr(init, '__whitelist__') and
                config.db.name in init.__whitelist__):
                pass
            else:
                if self.__should_skip_for(init):
                    return True
            try:
                resetwarnings()
                init.setUpAll()
            except:
                # skip tests if global setup fails
                ex = self.__exc_info()
                for test in self._tests:
                    result.addError(test, ex)
                return False
        try:
            resetwarnings()
            for test in self._tests:
                if result.shouldStop:
                    break
                test(result)
            return result
        finally:
            try:
                resetwarnings()
                if init is not None:
                    init.tearDownAll()
            except:
                result.addError(init, self.__exc_info())
                pass

    def __should_skip_for(self, cls):
        if hasattr(cls, '__requires__'):
            global requires
            if requires is None:
                from testing import requires
            def test_suite(): return 'ok'
            for requirement in cls.__requires__:
                check = getattr(requires, requirement)
                if check(test_suite)() != 'ok':
                    # The requirement will perform messaging.
                    return True
        if (hasattr(cls, '__unsupported_on__') and
            config.db.name in cls.__unsupported_on__):
            print "'%s' unsupported on DB implementation '%s'" % (
                cls.__class__.__name__, config.db.name)
            return True
        if (getattr(cls, '__only_on__', None) not in (None,config.db.name)):
            print "'%s' unsupported on DB implementation '%s'" % (
                cls.__class__.__name__, config.db.name)
            return True
        if (getattr(cls, '__skip_if__', False)):
            for c in getattr(cls, '__skip_if__'):
                if c():
                    print "'%s' skipped by %s" % (
                        cls.__class__.__name__, c.__name__)
                    return True
        for rule in getattr(cls, '__excluded_on__', ()):
            if _is_excluded(*rule):
                print "'%s' unsupported on DB %s version %s" % (
                    cls.__class__.__name__, config.db.name,
                    _server_version())
                return True
        return False


    def __exc_info(self):
        """Return a version of sys.exc_info() with the traceback frame
           minimised; usually the top level of the traceback frame is not
           needed.
           ripped off out of unittest module since its double __
        """
        exctype, excvalue, tb = sys.exc_info()
        if sys.platform[:4] == 'java': ## tracebacks look different in Jython
            return (exctype, excvalue, tb)
        return (exctype, excvalue, tb)

# monkeypatch
unittest.TestLoader.suiteClass = TTestSuite


class DevNullWriter(object):
    def write(self, msg):
        pass
    def flush(self):
        pass

def runTests(suite):
    verbose = config.options.verbose
    quiet = config.options.quiet
    orig_stdout = sys.stdout

    try:
        if not verbose or quiet:
            sys.stdout = DevNullWriter()
        # Py3K
        #else:
        #    # straight from the man:  
        #    # http://mail.python.org/pipermail/python-3000/2008-February/012144.html
        #    sys.stdout._encoding = 'utf-8'
        runner = unittest.TextTestRunner(verbosity = quiet and 1 or 2)
        return runner.run(suite)
    finally:
        if not verbose or quiet:
            sys.stdout = orig_stdout

def main(suite=None):
    if not suite:
        if sys.argv[1:]:
            suite =unittest.TestLoader().loadTestsFromNames(
                sys.argv[1:], __import__('__main__'))
        else:
            suite = unittest.TestLoader().loadTestsFromModule(
                __import__('__main__'))

    result = runTests(suite)
    sys.exit(not result.wasSuccessful())
