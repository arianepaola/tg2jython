# coding: utf-8
import decimal
import testenv; testenv.configure_for_tests()
import datetime, os, pickleable, re
from sqlalchemy import *
from sqlalchemy import exc, types, util, schema
from sqlalchemy.sql import operators
from testlib.testing import eq_
import sqlalchemy.engine.url as url
from sqlalchemy.databases import *

from testlib import *


class AdaptTest(TestBase):
    def testmsnvarchar(self):
        dialect = mssql.dialect()
        # run the test twice to ensure the caching step works too
        for x in range(0, 1):
            col = Column('', Unicode(length=10))
            dialect_type = col.type.dialect_impl(dialect)
            assert isinstance(dialect_type, mssql.MSNVarchar)
            eq_(dialect.type_compiler.process(dialect_type), 'NVARCHAR(10)')

    def testoracletimestamp(self):
        dialect = oracle.OracleDialect()
        t1 = oracle.OracleTimestamp
        t2 = oracle.OracleTimestamp()
        t3 = types.TIMESTAMP
        assert isinstance(dialect.type_descriptor(t1), oracle.OracleTimestamp)
        assert isinstance(dialect.type_descriptor(t2), oracle.OracleTimestamp)
        assert isinstance(dialect.type_descriptor(t3), oracle.OracleTimestamp)

    def testmysqlbinary(self):
        dialect = mysql.MySQLDialect()
        t1 = mysql.MSVarBinary
        t2 = mysql.MSVarBinary()
        assert isinstance(dialect.type_descriptor(t1), mysql.MSVarBinary)
        assert isinstance(dialect.type_descriptor(t2), mysql.MSVarBinary)

    def teststringadapt(self):
        """test that String with no size becomes TEXT, *all* others stay as varchar/String"""

        oracle_dialect = oracle.OracleDialect()
        mysql_dialect = mysql.MySQLDialect()
        postgres_dialect = postgres.PGDialect()
        firebird_dialect = firebird.FBDialect()

        for dialect, start, test in [
            (oracle_dialect, String(), String),
            (oracle_dialect, VARCHAR(), VARCHAR),
            (oracle_dialect, String(50), String),
            (oracle_dialect, Unicode(), Unicode),
            (oracle_dialect, UnicodeText(), oracle.OracleText),
            (oracle_dialect, NCHAR(), NCHAR),
            (oracle_dialect, oracle.OracleRaw(50), oracle.OracleRaw),
            (mysql_dialect, String(), mysql.MSString),
            (mysql_dialect, VARCHAR(), mysql.MSString),
            (mysql_dialect, String(50), mysql.MSString),
            (mysql_dialect, Unicode(), mysql.MSString),
            (mysql_dialect, UnicodeText(), mysql.MSText),
            (mysql_dialect, NCHAR(), mysql.MSNChar),
            (postgres_dialect, String(), String),
            (postgres_dialect, VARCHAR(), String),
            (postgres_dialect, String(50), String),
            (postgres_dialect, Unicode(), String),
            (postgres_dialect, UnicodeText(), Text),
            (postgres_dialect, NCHAR(), String),
#            (firebird_dialect, String(), firebird.FBString),
#            (firebird_dialect, VARCHAR(), firebird.FBString),
#            (firebird_dialect, String(50), firebird.FBString),
#            (firebird_dialect, Unicode(), firebird.FBString),
#            (firebird_dialect, UnicodeText(), firebird.FBText),
#            (firebird_dialect, NCHAR(), firebird.FBString),
        ]:
            assert isinstance(start.dialect_impl(dialect), test), "wanted %r got %r" % (test, start.dialect_impl(dialect))

    def test_uppercase_rendering(self):
        """Test that uppercase types from types.py always render as their type.
        
        As of SQLA 0.6, using an uppercase type means you want specifically that
        type.  If the database in use doesn't support that DDL, it (the DB backend) 
        should raise an error - it means you should be using a lowercased (genericized) type.
        
        """
        
        for dialect in [
                oracle.dialect(), 
                mysql.dialect(), 
                postgres.dialect(), 
                sqlite.dialect(), 
                sybase.dialect(), 
                informix.dialect(), 
                maxdb.dialect(), 
                mssql.dialect()]: # TODO when dialects are complete:  engines.all_dialects():
            for type_, expected in (
                (FLOAT, "FLOAT"),
                (NUMERIC, "NUMERIC"),
                (DECIMAL, "DECIMAL"),
                (INTEGER, "INTEGER"),
                (SMALLINT, "SMALLINT"),
                (TIMESTAMP, "TIMESTAMP"),
                (DATETIME, "DATETIME"),
                (DATE, "DATE"),
                (TIME, "TIME"),
                (CLOB, "CLOB"),
                (VARCHAR, "VARCHAR"),
                (NVARCHAR, ("NVARCHAR", "NATIONAL VARCHAR")),
                (CHAR, "CHAR"),
                (NCHAR, ("NCHAR", "NATIONAL CHAR")),
                (BLOB, "BLOB"),
                (BOOLEAN, ("BOOLEAN", "BOOL"))
            ):
                if isinstance(expected, str):
                    expected = (expected, )
                for exp in expected:
                    compiled = type_().compile(dialect=dialect)
                    if exp in compiled:
                        break
                else:
                    assert False, "%r matches none of %r for dialect %s" % (compiled, expected, dialect.name)
            

class UserDefinedTest(TestBase):
    """tests user-defined types."""

    def testprocessing(self):

        global users
        users.insert().execute(
            user_id=2, goofy='jack', goofy2='jack', goofy4=u'jack',
            goofy7=u'jack', goofy8=12, goofy9=12)
        users.insert().execute(
            user_id=3, goofy='lala', goofy2='lala', goofy4=u'lala',
            goofy7=u'lala', goofy8=15, goofy9=15)
        users.insert().execute(
            user_id=4, goofy='fred', goofy2='fred', goofy4=u'fred',
            goofy7=u'fred', goofy8=9, goofy9=9)

        l = users.select().execute().fetchall()
        for assertstr, assertint, assertint2, row in zip(
            ["BIND_INjackBIND_OUT", "BIND_INlalaBIND_OUT", "BIND_INfredBIND_OUT"],
            [1200, 1500, 900],
            [1800, 2250, 1350],
            l
        ):
            for col in row[1:5]:
                self.assertEquals(col, assertstr)
            self.assertEquals(row[5], assertint)
            self.assertEquals(row[6], assertint2)
            for col in row[3], row[4]:
                assert isinstance(col, unicode)

    def setUpAll(self):
        global users, metadata

        class MyType(types.UserDefinedType):
            def get_col_spec(self):
                return "VARCHAR(100)"
            def bind_processor(self, dialect):
                def process(value):
                    return "BIND_IN"+ value
                return process
            def result_processor(self, dialect):
                def process(value):
                    return value + "BIND_OUT"
                return process
            def adapt(self, typeobj):
                return typeobj()

        class MyDecoratedType(types.TypeDecorator):
            impl = String
            def bind_processor(self, dialect):
                impl_processor = super(MyDecoratedType, self).bind_processor(dialect) or (lambda value:value)
                def process(value):
                    return "BIND_IN"+ impl_processor(value)
                return process
            def result_processor(self, dialect):
                impl_processor = super(MyDecoratedType, self).result_processor(dialect) or (lambda value:value)
                def process(value):
                    return impl_processor(value) + "BIND_OUT"
                return process
            def copy(self):
                return MyDecoratedType()

        class MyNewUnicodeType(types.TypeDecorator):
            impl = Unicode

            def process_bind_param(self, value, dialect):
                return "BIND_IN" + value

            def process_result_value(self, value, dialect):
                return value + "BIND_OUT"

            def copy(self):
                return MyNewUnicodeType(self.impl.length)

        class MyNewIntType(types.TypeDecorator):
            impl = Integer

            def process_bind_param(self, value, dialect):
                return value * 10

            def process_result_value(self, value, dialect):
                return value * 10

            def copy(self):
                return MyNewIntType()

        class MyNewIntSubClass(MyNewIntType):
            def process_result_value(self, value, dialect):
                return value * 15

            def copy(self):
                return MyNewIntSubClass()

        class MyUnicodeType(types.TypeDecorator):
            impl = Unicode

            def bind_processor(self, dialect):
                impl_processor = super(MyUnicodeType, self).bind_processor(dialect) or (lambda value:value)

                def process(value):
                    return "BIND_IN"+ impl_processor(value)
                return process

            def result_processor(self, dialect):
                impl_processor = super(MyUnicodeType, self).result_processor(dialect) or (lambda value:value)
                def process(value):
                    return impl_processor(value) + "BIND_OUT"
                return process

            def copy(self):
                return MyUnicodeType(self.impl.length)

        metadata = MetaData(testing.db)
        users = Table('type_users', metadata,
            Column('user_id', Integer, primary_key = True),
            # totall custom type
            Column('goofy', MyType, nullable = False),

            # decorated type with an argument, so its a String
            Column('goofy2', MyDecoratedType(50), nullable = False),

            Column('goofy4', MyUnicodeType(50), nullable = False),
            Column('goofy7', MyNewUnicodeType(50), nullable = False),
            Column('goofy8', MyNewIntType, nullable = False),
            Column('goofy9', MyNewIntSubClass, nullable = False),
        )

        metadata.create_all()

    def tearDownAll(self):
        metadata.drop_all()

class ColumnsTest(TestBase, AssertsExecutionResults):

    def testcolumns(self):
        expectedResults = { 'int_column': 'int_column INTEGER',
                            'smallint_column': 'smallint_column SMALLINT',
                            'varchar_column': 'varchar_column VARCHAR(20)',
                            'numeric_column': 'numeric_column NUMERIC(12, 3)',
                            'float_column': 'float_column FLOAT(25)',
                          }

        db = testing.db
        if testing.against('oracle'):
            expectedResults['float_column'] = 'float_column NUMERIC(25, 2)'

        if testing.against('sqlite'):
            expectedResults['float_column'] = 'float_column FLOAT'
            
        if testing.against('maxdb'):
            expectedResults['numeric_column'] = (
                expectedResults['numeric_column'].replace('NUMERIC', 'FIXED'))

        if testing.against('mssql'):
            for key, value in expectedResults.items():
                expectedResults[key] = '%s NULL' % value

        testTable = Table('testColumns', MetaData(db),
            Column('int_column', Integer),
            Column('smallint_column', SmallInteger),
            Column('varchar_column', String(20)),
            Column('numeric_column', Numeric(12,3)),
            Column('float_column', Float(25)),
        )

        for aCol in testTable.c:
            self.assertEquals(
                expectedResults[aCol.name],
                db.dialect.ddl_compiler(db.dialect, schema.CreateTable(testTable)).\
                  get_column_specification(aCol))

class UnicodeTest(TestBase, AssertsExecutionResults):
    """tests the Unicode type.  also tests the TypeDecorator with instances in the types package."""

    def setUpAll(self):
        global unicode_table, metadata
        metadata = MetaData(testing.db)
        unicode_table = Table('unicode_table', metadata,
            Column('id', Integer, Sequence('uni_id_seq', optional=True), primary_key=True),
            Column('unicode_varchar', Unicode(250)),
            Column('unicode_text', UnicodeText),
            )
        metadata.create_all()
        
    def tearDownAll(self):
        metadata.drop_all()

    def tearDown(self):
        unicode_table.delete().execute()

    def test_round_trip(self):
        unicodedata = u"Alors vous imaginez ma surprise, au lever du jour, quand une drôle de petit voix m’a réveillé. Elle disait: « S’il vous plaît… dessine-moi un mouton! »"
        
        unicode_table.insert().execute(unicode_varchar=unicodedata,unicode_text=unicodedata)
        
        x = unicode_table.select().execute().fetchone()
        self.assert_(isinstance(x['unicode_varchar'], unicode) and x['unicode_varchar'] == unicodedata)
        self.assert_(isinstance(x['unicode_text'], unicode) and x['unicode_text'] == unicodedata)

    def test_union(self):
        """ensure compiler processing works for UNIONs"""

        unicodedata = u"Alors vous imaginez ma surprise, au lever du jour, quand une drôle de petit voix m’a réveillé. Elle disait: « S’il vous plaît… dessine-moi un mouton! »"

        unicode_table.insert().execute(unicode_varchar=unicodedata,unicode_text=unicodedata)
                                       
        x = union(select([unicode_table.c.unicode_varchar]), select([unicode_table.c.unicode_varchar])).execute().fetchone()
        self.assert_(isinstance(x['unicode_varchar'], unicode) and x['unicode_varchar'] == unicodedata)

    @testing.fails_on('oracle', 'oracle converts empty strings to a blank space')
    def test_blank_strings(self):
        unicode_table.insert().execute(unicode_varchar=u'')
        assert select([unicode_table.c.unicode_varchar]).scalar() == u''

    def test_parameters(self):
        """test the dialect convert_unicode parameters."""

        unicodedata = u"Alors vous imaginez ma surprise, au lever du jour, quand une drôle de petit voix m’a réveillé. Elle disait: « S’il vous plaît… dessine-moi un mouton! »"

        u = Unicode(assert_unicode=True)
        uni = u.dialect_impl(testing.db.dialect).bind_processor(testing.db.dialect)
        # Py3K
        #self.assertRaises(exc.InvalidRequestError, uni, b'x')
        # Py2K
        self.assertRaises(exc.InvalidRequestError, uni, 'x')
        # end Py2K

        u = Unicode()
        uni = u.dialect_impl(testing.db.dialect).bind_processor(testing.db.dialect)
        # Py3K
        #self.assertRaises(exc.SAWarning, uni, b'x')
        # Py2K
        self.assertRaises(exc.SAWarning, uni, 'x')
        # end Py2K

        unicode_engine = engines.utf8_engine(options={'convert_unicode':True,'assert_unicode':True})
        unicode_engine.dialect.supports_unicode_binds = False
        
        s = String()
        uni = s.dialect_impl(unicode_engine.dialect).bind_processor(unicode_engine.dialect)
        # Py3K
        #self.assertRaises(exc.InvalidRequestError, uni, b'x')
        #assert isinstance(uni(unicodedata), bytes)
        # Py2K
        self.assertRaises(exc.InvalidRequestError, uni, 'x')
        assert isinstance(uni(unicodedata), str)
        # end Py2K
        
        assert uni(unicodedata) == unicodedata.encode('utf-8')

class BinaryTest(TestBase, AssertsExecutionResults):
    __excluded_on__ = (
        ('mysql', '<', (4, 1, 1)),  # screwy varbinary types
        )

    def setUpAll(self):
        global binary_table, MyPickleType

        class MyPickleType(types.TypeDecorator):
            impl = PickleType

            def process_bind_param(self, value, dialect):
                if value:
                    value.stuff = 'this is modified stuff'
                return value

            def process_result_value(self, value, dialect):
                if value:
                    value.stuff = 'this is the right stuff'
                return value

        binary_table = Table('binary_table', MetaData(testing.db),
            Column('primary_id', Integer, Sequence('binary_id_seq', optional=True), primary_key=True),
            Column('data', Binary),
            Column('data_slice', Binary(100)),
            Column('misc', String(30)),
            # construct PickleType with non-native pickle module, since cPickle uses relative module
            # loading and confuses this test's parent package 'sql' with the 'sqlalchemy.sql' package relative
            # to the 'types' module
            Column('pickled', PickleType),
            Column('mypickle', MyPickleType)
        )
        binary_table.create()

    def tearDown(self):
        binary_table.delete().execute()

    def tearDownAll(self):
        binary_table.drop()

    @testing.fails_on('mssql', 'MSSQl BINARY type right pads the fixed length with \x00')
    def test_round_trip(self):
        testobj1 = pickleable.Foo('im foo 1')
        testobj2 = pickleable.Foo('im foo 2')
        testobj3 = pickleable.Foo('im foo 3')

        stream1 =self.load_stream('binary_data_one.dat')
        stream2 =self.load_stream('binary_data_two.dat')
        binary_table.insert().execute(
                            primary_id=1, 
                            misc='binary_data_one.dat', 
                            data=stream1, 
                            data_slice=stream1[0:100], 
                            pickled=testobj1, 
                            mypickle=testobj3)
        binary_table.insert().execute(
                            primary_id=2, 
                            misc='binary_data_two.dat', 
                            data=stream2, 
                            data_slice=stream2[0:99], 
                            pickled=testobj2)
        binary_table.insert().execute(
                            primary_id=3, 
                            misc='binary_data_two.dat', 
                            data=None, 
                            data_slice=stream2[0:99], 
                            pickled=None)

        for stmt in (
            binary_table.select(order_by=binary_table.c.primary_id),
            text("select * from binary_table order by binary_table.primary_id", typemap={'pickled':PickleType, 'mypickle':MyPickleType}, bind=testing.db)
        ):
            l = stmt.execute().fetchall()
            self.assertEquals(list(stream1), list(l[0]['data']))
            self.assertEquals(list(stream1[0:100]), list(l[0]['data_slice']))
            self.assertEquals(list(stream2), list(l[1]['data']))
            self.assertEquals(testobj1, l[0]['pickled'])
            self.assertEquals(testobj2, l[1]['pickled'])
            self.assertEquals(testobj3.moredata, l[0]['mypickle'].moredata)
            self.assertEquals(l[0]['mypickle'].stuff, 'this is the right stuff')

    def load_stream(self, name):
        f = os.path.join(os.path.dirname(testenv.__file__), name)
        return open(f, mode='rb').read()

class ExpressionTest(TestBase, AssertsExecutionResults):
    def setUpAll(self):
        global test_table, meta

        class MyCustomType(types.UserDefinedType):
            def get_col_spec(self):
                return "INT"
            def bind_processor(self, dialect):
                def process(value):
                    return value * 10
                return process
            def result_processor(self, dialect):
                def process(value):
                    return value / 10
                return process
            def adapt_operator(self, op):
                return {operators.add:operators.sub, operators.sub:operators.add}.get(op, op)

        meta = MetaData(testing.db)
        test_table = Table('test', meta,
            Column('id', Integer, primary_key=True),
            Column('data', String(30)),
            Column('atimestamp', Date),
            Column('avalue', MyCustomType))

        meta.create_all()

        test_table.insert().execute({'id':1, 'data':'somedata', 'atimestamp':datetime.date(2007, 10, 15), 'avalue':25})

    def tearDownAll(self):
        meta.drop_all()

    def test_control(self):
        assert testing.db.execute("select avalue from test").scalar() == 250

        assert test_table.select().execute().fetchall() == [(1, 'somedata', datetime.date(2007, 10, 15), 25)]

    def test_bind_adapt(self):
        expr = test_table.c.atimestamp == bindparam("thedate")
        assert expr.right.type.__class__ == test_table.c.atimestamp.type.__class__

        assert testing.db.execute(test_table.select().where(expr), {"thedate":datetime.date(2007, 10, 15)}).fetchall() == [(1, 'somedata', datetime.date(2007, 10, 15), 25)]

        expr = test_table.c.avalue == bindparam("somevalue")
        assert expr.right.type.__class__ == test_table.c.avalue.type.__class__
        assert testing.db.execute(test_table.select().where(expr), {"somevalue":25}).fetchall() == [(1, 'somedata', datetime.date(2007, 10, 15), 25)]

    @testing.fails_on('firebird', 'Data type unknown on the parameter')
    def test_operator_adapt(self):
        """test type-based overloading of operators"""

        # test string concatenation
        expr = test_table.c.data + "somedata"
        assert testing.db.execute(select([expr])).scalar() == "somedatasomedata"

        expr = test_table.c.id + 15
        assert testing.db.execute(select([expr])).scalar() == 16

        # test custom operator conversion
        expr = test_table.c.avalue + 40
        assert expr.type.__class__ is test_table.c.avalue.type.__class__

        # + operator converted to -
        # value is calculated as: (250 - (40 * 10)) / 10 == -15
        assert testing.db.execute(select([expr.label('foo')])).scalar() == -15

        # this one relies upon anonymous labeling to assemble result
        # processing rules on the column.
        assert testing.db.execute(select([expr])).scalar() == -15

class DateTest(TestBase, AssertsExecutionResults):
    def setUpAll(self):
        global users_with_date, insert_data

        db = testing.db
        if testing.against('oracle'):
            insert_data =  [
                    (7, 'jack',
                     datetime.datetime(2005, 11, 10, 0, 0),
                     datetime.date(2005,11,10),
                     datetime.datetime(2005, 11, 10, 0, 0, 0, 29384)),
                    (8, 'roy',
                     datetime.datetime(2005, 11, 10, 11, 52, 35),
                     datetime.date(2005,10,10),
                     datetime.datetime(2006, 5, 10, 15, 32, 47, 6754)),
                    (9, 'foo',
                     datetime.datetime(2006, 11, 10, 11, 52, 35),
                     datetime.date(1970,4,1),
                     datetime.datetime(2004, 9, 18, 4, 0, 52, 1043)),
                    (10, 'colber', None, None, None),
             ]
            fnames = ['user_id', 'user_name', 'user_datetime',
                      'user_date', 'user_time']

            collist = [Column('user_id', INT, primary_key=True),
                       Column('user_name', VARCHAR(20)),
                       Column('user_datetime', DateTime),
                       Column('user_date', Date),
                       Column('user_time', TIMESTAMP)]
        else:
            datetime_micro = 54839
            time_micro = 999

            # Missing or poor microsecond support:
            if testing.against('mssql', 'mysql', 'firebird'):
                datetime_micro, time_micro = 0, 0
            # No microseconds for TIME
            elif testing.against('maxdb'):
                time_micro = 0

            insert_data =  [
                (7, 'jack',
                 datetime.datetime(2005, 11, 10, 0, 0),
                 datetime.date(2005, 11, 10),
                 datetime.time(12, 20, 2)),
                (8, 'roy',
                 datetime.datetime(2005, 11, 10, 11, 52, 35),
                 datetime.date(2005, 10, 10),
                 datetime.time(0, 0, 0)),
                (9, 'foo',
                 datetime.datetime(2005, 11, 10, 11, 52, 35, datetime_micro),
                 datetime.date(1970, 4, 1),
                 datetime.time(23, 59, 59, time_micro)),
                (10, 'colber', None, None, None),
            ]
            
            
            fnames = ['user_id', 'user_name', 'user_datetime',
                      'user_date', 'user_time']

            collist = [Column('user_id', INT, primary_key=True),
                       Column('user_name', VARCHAR(20)),
                       Column('user_datetime', DateTime(timezone=False)),
                       Column('user_date', Date),
                       Column('user_time', Time)]

        if testing.against('sqlite', 'postgres'):
            insert_data.append(
                (11, 'historic',
                datetime.datetime(1850, 11, 10, 11, 52, 35, datetime_micro),
                datetime.date(1727,4,1),
                None),
            )

        users_with_date = Table('query_users_with_date',
                                MetaData(testing.db), *collist)
        users_with_date.create()
        insert_dicts = [dict(zip(fnames, d)) for d in insert_data]

        for idict in insert_dicts:
            users_with_date.insert().execute(**idict)

    def tearDownAll(self):
        users_with_date.drop()

    def testdate(self):
        global insert_data

        l = map(tuple, users_with_date.select().execute().fetchall())
        self.assert_(l == insert_data,
                     'DateTest mismatch: got:%s expected:%s' % (l, insert_data))

    def testtextdate(self):
        x = testing.db.text(
            "select user_datetime from query_users_with_date",
            typemap={'user_datetime':DateTime}).execute().fetchall()

        self.assert_(isinstance(x[0][0], datetime.datetime))

        x = testing.db.text(
            "select * from query_users_with_date where user_datetime=:somedate",
            bindparams=[bindparam('somedate', type_=types.DateTime)]).execute(
            somedate=datetime.datetime(2005, 11, 10, 11, 52, 35)).fetchall()

    def testdate2(self):
        meta = MetaData(testing.db)
        t = Table('testdate', meta,
                  Column('id', Integer,
                         Sequence('datetest_id_seq', optional=True),
                         primary_key=True),
                Column('adate', Date), Column('adatetime', DateTime))
        t.create(checkfirst=True)
        try:
            d1 = datetime.date(2007, 10, 30)
            t.insert().execute(adate=d1, adatetime=d1)
            d2 = datetime.datetime(2007, 10, 30)
            t.insert().execute(adate=d2, adatetime=d2)

            x = t.select().execute().fetchall()[0]
            self.assert_(x.adate.__class__ == datetime.date)
            self.assert_(x.adatetime.__class__ == datetime.datetime)

            t.delete().execute()

            # test mismatched date/datetime
            t.insert().execute(adate=d2, adatetime=d2)
            self.assertEquals(select([t.c.adate, t.c.adatetime], t.c.adate==d1).execute().fetchall(), [(d1, d2)])
            self.assertEquals(select([t.c.adate, t.c.adatetime], t.c.adate==d1).execute().fetchall(), [(d1, d2)])

        finally:
            t.drop(checkfirst=True)

class StringTest(TestBase, AssertsExecutionResults):
    @testing.fails_on('mysql', 'FIXME: unknown')
    @testing.fails_on('oracle', 'FIXME: unknown')
    def test_nolength_string(self):
        metadata = MetaData(testing.db)
        foo = Table('foo', metadata, Column('one', String))

        foo.create()
        foo.drop()

def _missing_decimal():
    """Python implementation supports decimals"""
    try:
        import decimal
        return False
    except ImportError:
        return True

class NumericTest(TestBase, AssertsExecutionResults):
    def setUpAll(self):
        global numeric_table, metadata
        metadata = MetaData(testing.db)
        numeric_table = Table('numeric_table', metadata,
            Column('id', Integer, Sequence('numeric_id_seq', optional=True), primary_key=True),
            Column('numericcol', Numeric(asdecimal=False)),
            Column('floatcol', Float),
            Column('ncasdec', Numeric),
            Column('fcasdec', Float(asdecimal=True))
        )
        metadata.create_all()

    def tearDownAll(self):
        metadata.drop_all()

    def tearDown(self):
        numeric_table.delete().execute()

    @testing.fails_if(_missing_decimal)
    def test_decimal(self):
        from decimal import Decimal
        numeric_table.insert().execute(
            numericcol=3.5, floatcol=5.6, ncasdec=12.4, fcasdec=15.75)
            
        numeric_table.insert().execute(
            numericcol=Decimal("3.5"), floatcol=Decimal("5.6"),
            ncasdec=Decimal("12.4"), fcasdec=Decimal("15.75"))

        l = numeric_table.select().execute().fetchall()
        print l
        rounded = [
            (l[0][0], l[0][1], round(l[0][2], 5), l[0][3], l[0][4]),
            (l[1][0], l[1][1], round(l[1][2], 5), l[1][3], l[1][4]),
        ]
        testing.eq_(rounded, [
            (1, 3.5, 5.6, Decimal("12.4"), Decimal("15.75")),
            (2, 3.5, 5.6, Decimal("12.4"), Decimal("15.75")),
        ])

    def test_decimal_fallback(self):
        from decimal import Decimal

        numeric_table.insert().execute(ncasdec=12.4, fcasdec=15.75)
        numeric_table.insert().execute(ncasdec=Decimal("12.4"),
                                       fcasdec=Decimal("15.75"))

        for row in numeric_table.select().execute().fetchall():
            assert isinstance(row['ncasdec'], decimal.Decimal)
            assert isinstance(row['fcasdec'], decimal.Decimal)

    def test_length_deprecation(self):
        self.assertRaises(exc.SADeprecationWarning, Numeric, length=8)
        
        @testing.uses_deprecated(".*is deprecated for Numeric")
        def go():
            n = Numeric(length=12)
            assert n.scale == 12
        go()
        
        n = Numeric(scale=12)
        for dialect in engines.all_dialects():
            n2 = dialect.type_descriptor(n)
            eq_(n2.scale, 12, dialect.name)
            
            # test colspec generates successfully using 'scale'
            assert dialect.type_compiler.process(n2)
            
            # test constructor of the dialect-specific type
            n3 = n2.__class__(scale=5)
            eq_(n3.scale, 5, dialect.name)
            
            @testing.uses_deprecated(".*is deprecated for Numeric")
            def go():
                n3 = n2.__class__(length=6)
                eq_(n3.scale, 6, dialect.name)
            go()
                
            
class IntervalTest(TestBase, AssertsExecutionResults):
    def setUpAll(self):
        global interval_table, metadata
        metadata = MetaData(testing.db)
        interval_table = Table("intervaltable", metadata,
            Column("id", Integer, Sequence('interval_id_seq', optional=True), primary_key=True),
            Column("interval", Interval),
            )
        metadata.create_all()

    def tearDown(self):
        interval_table.delete().execute()

    def tearDownAll(self):
        metadata.drop_all()

    @testing.fails_on("+pg8000", "Not yet known how to pass values of the INTERVAL type")
    def test_roundtrip(self):
        delta = datetime.datetime(2006, 10, 5) - datetime.datetime(2005, 8, 17)
        interval_table.insert().execute(interval=delta)
        assert interval_table.select().execute().fetchone()['interval'] == delta

    def test_null(self):
        interval_table.insert().execute(id=1, inverval=None)
        assert interval_table.select().execute().fetchone()['interval'] is None

class BooleanTest(TestBase, AssertsExecutionResults):
    def setUpAll(self):
        global bool_table
        metadata = MetaData(testing.db)
        bool_table = Table('booltest', metadata,
            Column('id', Integer, primary_key=True),
            Column('value', Boolean))
        bool_table.create()
    def tearDownAll(self):
        bool_table.drop()
    def testbasic(self):
        bool_table.insert().execute(id=1, value=True)
        bool_table.insert().execute(id=2, value=False)
        bool_table.insert().execute(id=3, value=True)
        bool_table.insert().execute(id=4, value=True)
        bool_table.insert().execute(id=5, value=True)

        res = bool_table.select(bool_table.c.value==True).execute().fetchall()
        print res
        assert(res==[(1, True),(3, True),(4, True),(5, True)])

        res2 = bool_table.select(bool_table.c.value==False).execute().fetchall()
        print res2
        assert(res2==[(2, False)])

class PickleTest(TestBase):
    def test_eq_comparison(self):
        p1 = PickleType()
        
        for obj in (
            {'1':'2'},
            pickleable.Bar(5, 6),
            pickleable.OldSchool(10, 11)
        ):
            assert p1.compare_values(p1.copy_value(obj), obj)

        self.assertRaises(NotImplementedError, p1.compare_values, pickleable.BrokenComparable('foo'),pickleable.BrokenComparable('foo'))
        
    def test_nonmutable_comparison(self):
        p1 = PickleType()

        for obj in (
            {'1':'2'},
            pickleable.Bar(5, 6),
            pickleable.OldSchool(10, 11)
        ):
            assert p1.compare_values(p1.copy_value(obj), obj)
    
class CallableTest(TestBase):
    def setUpAll(self):
        global meta
        meta = MetaData(testing.db)

    def tearDownAll(self):
        meta.drop_all()

    def test_callable_as_arg(self):
        ucode = util.partial(Unicode, assert_unicode=None)

        thing_table = Table('thing', meta,
            Column('name', ucode(20))
        )
        assert isinstance(thing_table.c.name.type, Unicode)
        thing_table.create()

    def test_callable_as_kwarg(self):
        ucode = util.partial(Unicode, assert_unicode=None)

        thang_table = Table('thang', meta,
            Column('name', type_=ucode(20), primary_key=True)
        )
        assert isinstance(thang_table.c.name.type, Unicode)
        thang_table.create()

if __name__ == "__main__":
    testenv.main()
