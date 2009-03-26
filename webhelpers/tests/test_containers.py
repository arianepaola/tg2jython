# -*- coding: utf-8 -*-
import os
import copy
import tempfile

from nose.tools import assert_equal, assert_raises

from webhelpers.containers import DumbObject
from webhelpers.containers import defaultdict as webhelpers_containers_defaultdict

# Tests from Python 2.5 test_defaultdict_defaultdict.py, as this is just a 2.4 backport
# anyway
def foobar():
    return list

def test_defaultdict_basic():
    d1 = webhelpers_containers_defaultdict()
    assert_equal(d1.default_factory, None)
    d1.default_factory = list
    d1[12].append(42)
    assert_equal(d1, {12: [42]})
    d1[12].append(24)
    assert_equal(d1, {12: [42, 24]})
    d1[13]
    d1[14]
    assert_equal(d1, {12: [42, 24], 13: [], 14: []})
    assert d1[12] is not d1[13] is not d1[14]
    d2 = webhelpers_containers_defaultdict(list, foo=1, bar=2)
    assert_equal(d2.default_factory, list)
    assert_equal(d2, {"foo": 1, "bar": 2})
    assert_equal(d2["foo"], 1)
    assert_equal(d2["bar"], 2)
    assert_equal(d2[42], [])
    assert "foo" in d2
    assert "foo" in d2.keys()
    assert "bar" in d2
    assert "bar" in d2.keys()
    assert 42 in d2
    assert 42 in d2.keys()
    assert 12 not in d2
    assert 12 not in d2.keys()
    d2.default_factory = None
    assert_equal(d2.default_factory, None)
    try:
        d2[15]
    except KeyError, err:
        assert_equal(err.args, (15,))
    else:
        message = "d2[15] didn't raise KeyError"
        raise AssertionError(message)

def test_defaultdict_missing():
    d1 = webhelpers_containers_defaultdict()
    assert_raises(KeyError, d1.__missing__, 42)
    d1.default_factory = list
    assert_equal(d1.__missing__(42), [])

def test_defaultdict_repr():
    d1 = webhelpers_containers_defaultdict()
    assert_equal(d1.default_factory, None)
    assert_equal(repr(d1), "defaultdict(None, {})")
    d1[11] = 41
    assert_equal(repr(d1), "defaultdict(None, {11: 41})")

def test_defaultdict_repr_2():
    def foo(): return 43
    d3 = webhelpers_containers_defaultdict(foo)
    assert d3.default_factory is foo
    d3[13]
    assert_equal(repr(d3), "defaultdict(%s, {13: 43})" % repr(foo))

def test_defaultdict_print():
    d1 = webhelpers_containers_defaultdict()
    def foo(): return 42
    d2 = webhelpers_containers_defaultdict(foo, {1: 2})
    # NOTE: We can't use tempfile.[Named]TemporaryFile since this
    # code must exercise the tp_print C code, which only gets
    # invoked for *real* files.
    tfn = tempfile.mktemp()
    try:
        f = open(tfn, "w+")
        try:
            print >>f, d1
            print >>f, d2
            f.seek(0)
            assert_equal(f.readline(), repr(d1) + "\n")
            assert_equal(f.readline(), repr(d2) + "\n")
        finally:
            f.close()
    finally:
        os.remove(tfn)

def test_defaultdict_copy():
    d1 = webhelpers_containers_defaultdict()
    d2 = d1.copy()
    assert_equal(type(d2), webhelpers_containers_defaultdict)
    assert_equal(d2.default_factory, None)
    assert_equal(d2, {})
    d1.default_factory = list
    d3 = d1.copy()
    assert_equal(type(d3), webhelpers_containers_defaultdict)
    assert_equal(d3.default_factory, list)
    assert_equal(d3, {})
    d1[42]
    d4 = d1.copy()
    assert_equal(type(d4), webhelpers_containers_defaultdict)
    assert_equal(d4.default_factory, list)
    assert_equal(d4, {42: []})
    d4[12]
    assert_equal(d4, {42: [], 12: []})

def test_defaultdict_shallow_copy():
    d1 = webhelpers_containers_defaultdict(foobar, {1: 1})
    d2 = copy.copy(d1)
    assert_equal(d2.default_factory, foobar)
    assert_equal(d2, d1)
    d1.default_factory = list
    d2 = copy.copy(d1)
    assert_equal(d2.default_factory, list)
    assert_equal(d2, d1)

def test_defaultdict_deep_copy():
    d1 = webhelpers_containers_defaultdict(foobar, {1: [1]})
    d2 = copy.deepcopy(d1)
    assert_equal(d2.default_factory, foobar)
    assert_equal(d2, d1)
    assert d1[1] is not d2[1]
    d1.default_factory = list
    d2 = copy.deepcopy(d1)
    assert_equal(d2.default_factory, list)
    assert_equal(d2, d1)

