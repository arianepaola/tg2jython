# types.py
# Copyright (C) 2005, 2006, 2007, 2008, 2009 Michael Bayer mike_mp@zzzcomputing.com
#
# This module is part of SQLAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""defines genericized SQL types, each represented by a subclass of
:class:`~sqlalchemy.types.AbstractType`.  Dialects define further subclasses of these
types.

For more information see the SQLAlchemy documentation on types.

"""
__all__ = [ 'TypeEngine', 'TypeDecorator', 'AbstractType',
            'INT', 'CHAR', 'VARCHAR', 'NCHAR', 'NVARCHAR','TEXT', 'Text', 'FLOAT',
            'NUMERIC', 'DECIMAL', 'TIMESTAMP', 'DATETIME', 'CLOB', 'BLOB',
            'BOOLEAN', 'SMALLINT', 'INTEGER','DATE', 'TIME',
            'String', 'Integer', 'SmallInteger',
            'Numeric', 'Float', 'DateTime', 'Date', 'Time', 'Binary',
            'Boolean', 'Unicode', 'MutableType', 'Concatenable', 'UnicodeText', 'PickleType', 'Interval',
            'type_map'
            ]

import inspect
import datetime as dt
from decimal import Decimal as _python_Decimal

from sqlalchemy import exc
from sqlalchemy.util import pickle
from sqlalchemy.sql.visitors import Visitable
from sqlalchemy.sql import expression
import sys
expression.sqltypes = sys.modules[__name__]
import sqlalchemy.util as util
NoneType = type(None)
    
class AbstractType(Visitable):

    def __init__(self, *args, **kwargs):
        pass

    def compile(self, dialect):
        return dialect.type_compiler.process(self)
        
    def copy_value(self, value):
        return value

    def bind_processor(self, dialect):
        """Defines a bind parameter processing function."""

        return None

    def result_processor(self, dialect):
        """Defines a result-column processing function."""

        return None

    def compare_values(self, x, y):
        """Compare two values for equality."""

        return x == y

    def is_mutable(self):
        """Return True if the target Python type is 'mutable'.

        This allows systems like the ORM to know if a column value can
        be considered 'not changed' by comparing the identity of
        objects alone.

        Use the :class:`MutableType` mixin or override this method to
        return True in custom types that hold mutable values such as
        ``dict``, ``list`` and custom objects.

        """
        return False

    def get_dbapi_type(self, dbapi):
        """Return the corresponding type object from the underlying DB-API, if any.

        This can be useful for calling ``setinputsizes()``, for example.
        """
        return None

    def adapt_operator(self, op):
        """Given an operator from the sqlalchemy.sql.operators package,
        translate it to a new operator based on the semantics of this type.

        By default, returns the operator unchanged.
        """
        return op

    def get_search_list(self):
        """return a list of classes to test for a match
        when adapting this type to a dialect-specific type.

        """

        return self.__class__.__mro__[0:-1]

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            ", ".join("%s=%r" % (k, getattr(self, k, None))
                      for k in inspect.getargspec(self.__init__)[0][1:]))

class TypeEngine(AbstractType):
    """Base for built-in types."""

    def dialect_impl(self, dialect, **kwargs):
        try:
            return self._impl_dict[dialect.__class__]
        except AttributeError:
            self._impl_dict = {}
            return self._impl_dict.setdefault(dialect.__class__, dialect.__class__.type_descriptor(self))
        except KeyError:
            return self._impl_dict.setdefault(dialect.__class__, dialect.__class__.type_descriptor(self))

    def __getstate__(self):
        d = self.__dict__.copy()
        d['_impl_dict'] = {}
        return d

    def bind_processor(self, dialect):
        """Return a conversion function for processing bind values.

        Returns a callable which will receive a bind parameter value
        as the sole positional argument and will return a value to
        send to the DB-API.

        If processing is not necessary, the method should return ``None``.

        """
        return None

    def result_processor(self, dialect):
        """Return a conversion function for processing result row values.

        Returns a callable which will receive a result row column
        value as the sole positional argument and will return a value
        to return to the user.

        If processing is not necessary, the method should return ``None``.

        """
        return None

    def adapt(self, cls):
        return cls()

class UserDefinedType(TypeEngine):
    """Base for user defined types.
    
    This should be the base of new types.  Note that
    for most cases, :class:`TypeDecorator` is probably
    more appropriate.

      import sqlalchemy.types as types

      class MyType(types.UserDefinedType):
          def __init__(self, precision = 8):
              self.precision = precision

          def get_col_spec(self):
              return "MYTYPE(%s)" % self.precision

          def bind_processor(self, dialect):
              def process(value):
                  return value
              return process

          def result_processor(self, dialect):
              def process(value):
                  return value
              return process

    Once the type is made, it's immediately usable::

      table = Table('foo', meta,
          Column('id', Integer, primary_key=True),
          Column('data', MyType(16))
          )

    """
    __visit_name__ = "user_defined"
    
class TypeDecorator(AbstractType):
    """Allows the creation of types which add additional functionality
    to an existing type.

    Typical usage::

      import sqlalchemy.types as types

      class MyType(types.TypeDecorator):
          # Prefixes Unicode values with "PREFIX:" on the way in and
          # strips it off on the way out.

          impl = types.Unicode

          def process_bind_param(self, value, dialect):
              return "PREFIX:" + value

          def process_result_value(self, value, dialect):
              return value[7:]

          def copy(self):
              return MyType(self.impl.length)

    The class-level "impl" variable is required, and can reference any
    TypeEngine class.  Alternatively, the load_dialect_impl() method
    can be used to provide different type classes based on the dialect
    given; in this case, the "impl" variable can reference
    ``TypeEngine`` as a placeholder.

    The reason that type behavior is modified using class decoration
    instead of subclassing is due to the way dialect specific types
    are used.  Such as with the example above, when using the mysql
    dialect, the actual type in use will be a
    ``sqlalchemy.databases.mysql.MSString`` instance.
    ``TypeDecorator`` handles the mechanics of passing the values
    between user-defined ``process_`` methods and the current
    dialect-specific type in use.

    """

    __visit_name__ = "type_decorator"
    
    def __init__(self, *args, **kwargs):
        if not hasattr(self.__class__, 'impl'):
            raise AssertionError("TypeDecorator implementations require a class-level variable 'impl' which refers to the class of type being decorated")
        self.impl = self.__class__.impl(*args, **kwargs)

    def dialect_impl(self, dialect):
        try:
            return self._impl_dict[dialect.__class__]
        except AttributeError:
            self._impl_dict = {}
        except KeyError:
            pass

        # adapt the TypeDecorator first, in 
        # the case that the dialect maps the TD
        # to one of its native types (i.e. PGInterval)
        adapted = dialect.__class__.type_descriptor(self)
        if adapted is not self:
            self._impl_dict[dialect] = adapted
            return adapted
        
        # otherwise adapt the impl type, link
        # to a copy of this TypeDecorator and return
        # that.
        typedesc = self.load_dialect_impl(dialect)
        tt = self.copy()
        if not isinstance(tt, self.__class__):
            raise AssertionError("Type object %s does not properly implement the copy() "
                    "method, it must return an object of type %s" % (self, self.__class__))
        tt.impl = typedesc
        self._impl_dict[dialect] = tt
        return tt

    def type_engine(self, dialect):
        impl = self.dialect_impl(dialect)
        if not isinstance(impl, TypeDecorator):
            return impl
        else:
            return impl.impl

    def load_dialect_impl(self, dialect):
        """Loads the dialect-specific implementation of this type.

        by default calls dialect.type_descriptor(self.impl), but
        can be overridden to provide different behavior.
        
        """
        if isinstance(self.impl, TypeDecorator):
            return self.impl.dialect_impl(dialect)
        else:
            return dialect.__class__.type_descriptor(self.impl)

    def __getattr__(self, key):
        """Proxy all other undefined accessors to the underlying implementation."""

        return getattr(self.impl, key)

    def process_bind_param(self, value, dialect):
        raise NotImplementedError()

    def process_result_value(self, value, dialect):
        raise NotImplementedError()

    def bind_processor(self, dialect):
        if self.__class__.process_bind_param.func_code is not TypeDecorator.process_bind_param.func_code:
            impl_processor = self.impl.bind_processor(dialect)
            if impl_processor:
                def process(value):
                    return impl_processor(self.process_bind_param(value, dialect))
                return process
            else:
                def process(value):
                    return self.process_bind_param(value, dialect)
                return process
        else:
            return self.impl.bind_processor(dialect)

    def result_processor(self, dialect):
        if self.__class__.process_result_value.func_code is not TypeDecorator.process_result_value.func_code:
            impl_processor = self.impl.result_processor(dialect)
            if impl_processor:
                def process(value):
                    return self.process_result_value(impl_processor(value), dialect)
                return process
            else:
                def process(value):
                    return self.process_result_value(value, dialect)
                return process
        else:
            return self.impl.result_processor(dialect)

    def copy(self):
        instance = self.__class__.__new__(self.__class__)
        instance.__dict__.update(self.__dict__)
        return instance

    def get_dbapi_type(self, dbapi):
        return self.impl.get_dbapi_type(dbapi)

    def copy_value(self, value):
        return self.impl.copy_value(value)

    def compare_values(self, x, y):
        return self.impl.compare_values(x, y)

    def is_mutable(self):
        return self.impl.is_mutable()

class MutableType(object):
    """A mixin that marks a Type as holding a mutable object.

    :meth:`copy_value` and :meth:`compare_values` should be customized
    as needed to match the needs of the object.

    """

    def is_mutable(self):
        """Return True, mutable."""
        return True

    def copy_value(self, value):
        """Unimplemented."""
        raise NotImplementedError()

    def compare_values(self, x, y):
        """Compare *x* == *y*."""
        return x == y

def to_instance(typeobj):
    if typeobj is None:
        return NULLTYPE

    try: 
        return typeobj()
    except TypeError:
        return typeobj

def adapt_type(typeobj, colspecs):
    if isinstance(typeobj, type):
        typeobj = typeobj()
    for t in typeobj.get_search_list():
        try:
            impltype = colspecs[t]
            break
        except KeyError:
            pass
    else:
        # couldnt adapt - so just return the type itself
        # (it may be a user-defined type)
        return typeobj
    # if we adapted the given generic type to a database-specific type,
    # but it turns out the originally given "generic" type
    # is actually a subclass of our resulting type, then we were already
    # given a more specific type than that required; so use that.
    if (issubclass(typeobj.__class__, impltype)):
        return typeobj
    return typeobj.adapt(impltype)

class NullType(TypeEngine):
    """An unknown type.

    NullTypes will stand in if :class:`~sqlalchemy.Table` reflection
    encounters a column data type unknown to SQLAlchemy.  The
    resulting columns are nearly fully usable: the DB-API adapter will
    handle all translation to and from the database data type.

    NullType does not have sufficient information to particpate in a
    ``CREATE TABLE`` statement and will raise an exception if
    encountered during a :meth:`~sqlalchemy.Table.create` operation.

    """
    __visit_name__ = 'null'

NullTypeEngine = NullType

class Concatenable(object):
    """A mixin that marks a type as supporting 'concatenation', typically strings."""

    def adapt_operator(self, op):
        """Converts an add operator to concat."""
        from sqlalchemy.sql import operators
        if op is operators.add:
            return operators.concat_op
        else:
            return op

class String(Concatenable, TypeEngine):
    """The base for all string and character types.

    In SQL, corresponds to VARCHAR.  Can also take Python unicode objects
    and encode to the database's encoding in bind params (and the reverse for
    result sets.)

    The `length` field is usually required when the `String` type is
    used within a CREATE TABLE statement, as VARCHAR requires a length
    on most databases.

    """

    __visit_name__ = 'string'
    
    def __init__(self, length=None, convert_unicode=False, assert_unicode=None):
        """
        Create a string-holding type.

        :param length: optional, a length for the column for use in
          DDL statements.  May be safely omitted if no ``CREATE
          TABLE`` will be issued.  Certain databases may require a
          *length* for use in DDL, and will raise an exception when
          the ``CREATE TABLE`` DDL is issued.  Whether the value is
          interpreted as bytes or characters is database specific.

        :param convert_unicode: defaults to False.  If True, convert
          ``unicode`` data sent to the database to a ``str``
          bytestring, and convert bytestrings coming back from the
          database into ``unicode``.

          Bytestrings are encoded using the dialect's
          :attr:`~sqlalchemy.engine.base.Dialect.encoding`, which
          defaults to `utf-8`.

          If False, may be overridden by
          :attr:`sqlalchemy.engine.base.Dialect.convert_unicode`.

        :param assert_unicode:

          If None (the default), no assertion will take place unless
          overridden by :attr:`sqlalchemy.engine.base.Dialect.assert_unicode`.

          If 'warn', will issue a runtime warning if a ``str``
          instance is used as a bind value.

          If true, will raise an :exc:`sqlalchemy.exc.InvalidRequestError`.

        """
        self.length = length
        self.convert_unicode = convert_unicode
        self.assert_unicode = assert_unicode

    def adapt(self, impltype):
        return impltype(
                    length=self.length, 
                    convert_unicode=self.convert_unicode, 
                    assert_unicode=self.assert_unicode)

    def bind_processor(self, dialect):
        if self.convert_unicode or dialect.convert_unicode:
            if self.assert_unicode is None:
                assert_unicode = dialect.assert_unicode
            else:
                assert_unicode = self.assert_unicode
            
            if dialect.supports_unicode_binds and assert_unicode:
                def process(value):
                    if not isinstance(value, (unicode, NoneType)):
                        if assert_unicode == 'warn':
                            util.warn("Unicode type received non-unicode bind "
                                      "param value %r" % value)
                            return value
                        else:
                            raise exc.InvalidRequestError("Unicode type received non-unicode bind param value %r" % value)
                    else:
                        return value
            elif dialect.supports_unicode_binds:
                return None
            else:
                def process(value):
                    if isinstance(value, unicode):
                        return value.encode(dialect.encoding)
                    elif assert_unicode and not isinstance(value, (unicode, NoneType)):
                        if assert_unicode == 'warn':
                            util.warn("Unicode type received non-unicode bind "
                                      "param value %r" % value)
                            return value
                        else:
                            raise exc.InvalidRequestError("Unicode type received non-unicode bind param value %r" % value)
                    else:
                        return value
            return process
        else:
            return None

    def result_processor(self, dialect):
        if self.convert_unicode or dialect.convert_unicode:
            def process(value):
                if value is not None and not isinstance(value, unicode):
                    return value.decode(dialect.encoding)
                else:
                    return value
            return process
        else:
            return None

    def get_dbapi_type(self, dbapi):
        return dbapi.STRING

class Text(String):
    """A variably sized string type.

    In SQL, usually corresponds to CLOB or TEXT. Can also take Python
    unicode objects and encode to the database's encoding in bind
    params (and the reverse for result sets.)

    """
    __visit_name__ = 'text'

class Unicode(String):
    """A variable length Unicode string.

    The ``Unicode`` type is a :class:`String` which converts Python
    ``unicode`` objects (i.e., strings that are defined as
    ``u'somevalue'``) into encoded bytestrings when passing the value
    to the database driver, and similarly decodes values from the
    database back into Python ``unicode`` objects.

    When using the ``Unicode`` type, it is only appropriate to pass
    Python ``unicode`` objects, and not plain ``str``.  If a
    bytestring (``str``) is passed, a runtime warning is issued.  If
    you notice your application raising these warnings but you're not
    sure where, the Python ``warnings`` filter can be used to turn
    these warnings into exceptions which will illustrate a stack
    trace::

      import warnings
      warnings.simplefilter('error')

    Bytestrings sent to and received from the database are encoded
    using the dialect's
    :attr:`~sqlalchemy.engine.base.Dialect.encoding`, which defaults
    to `utf-8`.

    A synonym for String(length, convert_unicode=True, assert_unicode='warn').

    """

    def __init__(self, length=None, **kwargs):
        """
        Create a Unicode-converting String type.

        :param length: optional, a length for the column for use in
          DDL statements.  May be safely omitted if no ``CREATE
          TABLE`` will be issued.  Certain databases may require a
          *length* for use in DDL, and will raise an exception when
          the ``CREATE TABLE`` DDL is issued.  Whether the value is
          interpreted as bytes or characters is database specific.

        """
        kwargs.setdefault('convert_unicode', True)
        kwargs.setdefault('assert_unicode', 'warn')
        super(Unicode, self).__init__(length=length, **kwargs)

class UnicodeText(Text):
    """A synonym for Text(convert_unicode=True, assert_unicode='warn')."""

    def __init__(self, length=None, **kwargs):
        """
        Create a Unicode-converting Text type.

        :param length: optional, a length for the column for use in
          DDL statements.  May be safely omitted if no ``CREATE
          TABLE`` will be issued.  Certain databases may require a
          *length* for use in DDL, and will raise an exception when
          the ``CREATE TABLE`` DDL is issued.  Whether the value is
          interpreted as bytes or characters is database specific.

        """
        kwargs.setdefault('convert_unicode', True)
        kwargs.setdefault('assert_unicode', 'warn')
        super(UnicodeText, self).__init__(length=length, **kwargs)


class Integer(TypeEngine):
    """A type for ``int`` integers."""
    
    __visit_name__ = 'integer'
    
    def get_dbapi_type(self, dbapi):
        return dbapi.NUMBER


class SmallInteger(Integer):
    """A type for smaller ``int`` integers.

    Typically generates a ``SMALLINT`` in DDL, and otherwise acts like
    a normal :class:`Integer` on the Python side.

    """

    __visit_name__ = 'small_integer'

class BigInteger(Integer):
    """A type for bigger ``int`` integers.

    Typically generates a ``BIGINT`` in DDL, and otherwise acts like
    a normal :class:`Integer` on the Python side.

    """

    __visit_name__ = 'big_integer'

class Numeric(TypeEngine):
    """A type for fixed precision numbers.

    Typically generates DECIMAL or NUMERIC.  Returns
    ``decimal.Decimal`` objects by default.

    """

    __visit_name__ = 'numeric'
    
    def __init__(self, precision=10, scale=2, asdecimal=True, length=None):
        """
        Construct a Numeric.

        :param precision: the numeric precision for use in DDL ``CREATE TABLE``.

        :param scale: the numeric scale for use in DDL ``CREATE TABLE``.

        :param asdecimal: default True.  If False, values will be
          returned as-is from the DB-API, and may be either
          ``Decimal`` or ``float`` types depending on the DB-API in
          use.

        """
        if length:
            util.warn_deprecated("'length' is deprecated for Numeric.  Use 'scale'.")
            scale = length
        self.precision = precision
        self.scale = scale
        self.asdecimal = asdecimal

    def adapt(self, impltype):
        return impltype(precision=self.precision, scale=self.scale, asdecimal=self.asdecimal)

    def get_dbapi_type(self, dbapi):
        return dbapi.NUMBER

    def bind_processor(self, dialect):
        def process(value):
            if value is not None:
                return float(value)
            else:
                return value
        return process

    def result_processor(self, dialect):
        if self.asdecimal:
            def process(value):
                if value is not None:
                    return _python_Decimal(str(value))
                else:
                    return value
            return process
        else:
            return None


class Float(Numeric):
    """A type for ``float`` numbers."""

    __visit_name__ = 'float'
    
    def __init__(self, precision=10, asdecimal=False, **kwargs):
        """
        Construct a Float.

        :param precision: the numeric precision for use in DDL ``CREATE TABLE``.

        """
        self.precision = precision
        self.asdecimal = asdecimal

    def adapt(self, impltype):
        return impltype(precision=self.precision, asdecimal=self.asdecimal)


class DateTime(TypeEngine):
    """A type for ``datetime.datetime()`` objects.

    Date and time types return objects from the Python ``datetime``
    module.  Most DBAPIs have built in support for the datetime
    module, with the noted exception of SQLite.  In the case of
    SQLite, date and time types are stored as strings which are then
    converted back to datetime objects when rows are returned.

    """
    
    __visit_name__ = 'datetime'
    
    def __init__(self, timezone=False):
        self.timezone = timezone

    def adapt(self, impltype):
        return impltype(timezone=self.timezone)

    def get_dbapi_type(self, dbapi):
        return dbapi.DATETIME


class Date(TypeEngine):
    """A type for ``datetime.date()`` objects."""

    __visit_name__ = 'date'
    
    def get_dbapi_type(self, dbapi):
        return dbapi.DATETIME


class Time(TypeEngine):
    """A type for ``datetime.time()`` objects."""

    __visit_name__ = 'time'

    def __init__(self, timezone=False):
        self.timezone = timezone

    def adapt(self, impltype):
        return impltype(timezone=self.timezone)

    def get_dbapi_type(self, dbapi):
        return dbapi.DATETIME


class Binary(TypeEngine):
    """A type for binary byte data.

    The Binary type generates BLOB or BYTEA when tables are created,
    and also converts incoming values using the ``Binary`` callable
    provided by each DB-API.

    """

    __visit_name__ = 'binary'

    def __init__(self, length=None):
        """
        Construct a Binary type.

        :param length: optional, a length for the column for use in
          DDL statements.  May be safely omitted if no ``CREATE
          TABLE`` will be issued.  Certain databases may require a
          *length* for use in DDL, and will raise an exception when
          the ``CREATE TABLE`` DDL is issued.

        """
        self.length = length

    def bind_processor(self, dialect):
        DBAPIBinary = dialect.dbapi.Binary
        def process(value):
            if value is not None:
                return DBAPIBinary(value)
            else:
                return None
        return process

    def adapt(self, impltype):
        return impltype(length=self.length)

    def get_dbapi_type(self, dbapi):
        return dbapi.BINARY


class PickleType(MutableType, TypeDecorator):
    """Holds Python objects.

    PickleType builds upon the Binary type to apply Python's
    ``pickle.dumps()`` to incoming objects, and ``pickle.loads()`` on
    the way out, allowing any pickleable Python object to be stored as
    a serialized binary field.

    """

    impl = Binary

    def __init__(self, protocol=pickle.HIGHEST_PROTOCOL, pickler=None, mutable=True, comparator=None):
        """
        Construct a PickleType.

        :param protocol: defaults to ``pickle.HIGHEST_PROTOCOL``.

        :param pickler: defaults to cPickle.pickle or pickle.pickle if
          cPickle is not available.  May be any object with
          pickle-compatible ``dumps` and ``loads`` methods.

        :param mutable: defaults to True; implements
          :meth:`AbstractType.is_mutable`.   When ``True``, incoming
          objects *must* provide an ``__eq__()`` method which 
          performs the desired deep comparison of members, or the 
          ``comparator`` argument must be present.  Otherwise,
          comparisons are done by comparing pickle strings.
          The pickle form of comparison is a deprecated usage and will
          raise a warning.

        :param comparator: optional. a 2-arg callable predicate used
          to compare values of this type.  Otherwise, either
          the == operator is used to compare values, or if mutable==True
          and the incoming object does not implement __eq__(), the value
          of pickle.dumps(obj) is compared.  The last option is a deprecated
          usage and will raise a warning.

        """
        self.protocol = protocol
        self.pickler = pickler or pickle
        self.mutable = mutable
        self.comparator = comparator
        super(PickleType, self).__init__()

    def process_bind_param(self, value, dialect):
        dumps = self.pickler.dumps
        protocol = self.protocol
        if value is None:
            return None
        return dumps(value, protocol)

    def process_result_value(self, value, dialect):
        loads = self.pickler.loads
        if value is None:
            return None
        # Py3K
        #return loads(value)
        # Py2K
        return loads(str(value))
        # end Py2K

    def copy_value(self, value):
        if self.mutable:
            return self.pickler.loads(self.pickler.dumps(value, self.protocol))
        else:
            return value

    def compare_values(self, x, y):
        if self.comparator:
            return self.comparator(x, y)
        else:
            return x == y

    def is_mutable(self):
        return self.mutable


class Boolean(TypeEngine):
    """A bool datatype.

    Boolean typically uses BOOLEAN or SMALLINT on the DDL side, and on
    the Python side deals in ``True`` or ``False``.

    """

    __visit_name__ = 'boolean'

class Interval(TypeDecorator):
    """A type for ``datetime.timedelta()`` objects.

    The Interval type deals with ``datetime.timedelta`` objects.  In
    PostgreSQL, the native ``INTERVAL`` type is used; for others, the
    value is stored as a date which is relative to the "epoch"
    (Jan. 1, 1970).

    """

    impl = DateTime

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return dt.datetime.utcfromtimestamp(0) + value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value - dt.datetime.utcfromtimestamp(0)

class FLOAT(Float):
    """The SQL FLOAT type."""

    __visit_name__ = 'FLOAT'

class NUMERIC(Numeric):
    """The SQL NUMERIC type."""

    __visit_name__ = 'NUMERIC'


class DECIMAL(Numeric):
    """The SQL DECIMAL type."""

    __visit_name__ = 'DECIMAL'


class INTEGER(Integer):
    """The SQL INT or INTEGER type."""

    __visit_name__ = 'INTEGER'
INT = INTEGER


class SMALLINT(SmallInteger):
    """The SQL SMALLINT type."""

    __visit_name__ = 'SMALLINT'


class BIGINT(SmallInteger):
    """The SQL BIGINT type."""

    __visit_name__ = 'BIGINT'

class TIMESTAMP(DateTime):
    """The SQL TIMESTAMP type."""

    __visit_name__ = 'TIMESTAMP'

    def get_dbapi_type(self, dbapi):
        return dbapi.TIMESTAMP

class DATETIME(DateTime):
    """The SQL DATETIME type."""

    __visit_name__ = 'DATETIME'


class DATE(Date):
    """The SQL DATE type."""

    __visit_name__ = 'DATE'


class TIME(Time):
    """The SQL TIME type."""

    __visit_name__ = 'TIME'

class TEXT(Text):
    """The SQL TEXT type."""
    
    __visit_name__ = 'TEXT'

class CLOB(Text):
    """The SQL CLOB type."""

    __visit_name__ = 'CLOB'


class VARCHAR(String):
    """The SQL VARCHAR type."""

    __visit_name__ = 'VARCHAR'

class NVARCHAR(Unicode):
    """The SQL NVARCHAR type."""

    __visit_name__ = 'NVARCHAR'

class CHAR(String):
    """The SQL CHAR type."""

    __visit_name__ = 'CHAR'


class NCHAR(Unicode):
    """The SQL NCHAR type."""

    __visit_name__ = 'NCHAR'


class BLOB(Binary):
    """The SQL BLOB type."""

    __visit_name__ = 'BLOB'


class BOOLEAN(Boolean):
    """The SQL BOOLEAN type."""

    __visit_name__ = 'BOOLEAN'

NULLTYPE = NullType()

# using VARCHAR/NCHAR so that we dont get the genericized "String"
# type which usually resolves to TEXT/CLOB
type_map = {
    str : VARCHAR,
    # Py2K
    unicode : NCHAR,
    # end Py2K
    int : Integer,
    float : Numeric,
    bool: Boolean,
    _python_Decimal : Numeric,
    dt.date : Date,
    dt.datetime : DateTime,
    dt.time : Time,
    dt.timedelta : Interval,
    type(None): NullType
}

