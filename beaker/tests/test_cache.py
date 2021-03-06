# coding: utf-8
import time
from beaker.middleware import CacheMiddleware
from beaker.cache import Cache
from webtest import TestApp

def simple_app(environ, start_response):
    clear = False
    if environ.get('beaker.clear'):
        clear = True
    cache = environ['beaker.cache'].get_cache('testcache')
    if clear:
        cache.clear()
    try:
        value = cache.get_value('value')
    except:
        value = 0
    cache.set_value('value', value+1)
    start_response('200 OK', [('Content-type', 'text/plain')])
    return ['The current value is: %s' % cache.get_value('value')]

def cache_manager_app(environ, start_response):
    cm = environ['beaker.cache']
    cm.get_cache('test')['test_key'] = 'test value'

    start_response('200 OK', [('Content-type', 'text/plain')])
    yield "test_key is: %s\n" % cm.get_cache('test')['test_key']
    cm.get_cache('test').clear()

    try:
        test_value = cm.get_cache('test')['test_key']
    except KeyError:
        yield "test_key cleared"
    else:
        yield "test_key wasn't cleared, is: %s\n" % \
            cm.get_cache('test')['test_key']

def test_has_key():
    cache = Cache('test', data_dir='./cache', type='dbm')
    o = object()
    cache.set_value("test", o)
    assert cache.has_key("test")
    assert "test" in cache
    assert not cache.has_key("foo")
    assert "foo" not in cache
    cache.remove_value("test")
    assert not cache.has_key("test")

def test_expire_changes():
    cache = Cache('test', data_dir='./cache', type='dbm')
    cache.set_value('test', 10)
    assert cache.has_key('test')
    assert cache['test'] == 10
    assert cache._values['test'].expiretime is None
    
    # ensure that we can change a never-expiring value
    cache.set_value('test', 20, expiretime=1)
    assert cache.has_key('test')
    assert cache['test'] == 20
    assert cache._values['test'].expiretime == 1
    time.sleep(1)
    assert not cache.has_key('test')
    
    # test that we can change it before its expired
    cache.set_value('test', 30, expiretime=50)
    assert cache.has_key('test')
    assert cache['test'] == 30
    assert cache._values['test'].expiretime == 50
    
    cache.set_value('test', 40, expiretime=3)
    assert cache.has_key('test')
    assert cache['test'] == 40
    assert cache._values['test'].expiretime == 3
    time.sleep(3)
    assert not cache.has_key('test')

def test_fresh_createfunc():
    cache = Cache('test', data_dir='./cache', type='dbm')
    x = cache.get_value('test', createfunc=lambda: 10, expiretime=2)
    assert x == 10
    x = cache.get_value('test', createfunc=lambda: 12, expiretime=2)
    assert x == 10
    x = cache.get_value('test', createfunc=lambda: 14, expiretime=2)
    assert x == 10
    time.sleep(2)
    x = cache.get_value('test', createfunc=lambda: 16, expiretime=2)
    assert x == 16
    x = cache.get_value('test', createfunc=lambda: 18, expiretime=2)
    assert x == 16
    
    cache.remove_value('test')
    assert not cache.has_key('test')
    x = cache.get_value('test', createfunc=lambda: 20, expiretime=2)
    assert x == 20
    
    
    
def test_has_key_multicache():
    cache = Cache('test', data_dir='./cache', type='dbm')
    o = object()
    cache.set_value("test", o)
    assert cache.has_key("test")
    assert "test" in cache
    cache = Cache('test', data_dir='./cache', type='dbm')
    assert cache.has_key("test")

def test_unicode_keys():    
    cache = Cache('test', data_dir='./cache', type='dbm')
    o = object()
    cache.set_value(u'hiŏ', o)
    assert u'hiŏ' in cache
    assert u'hŏa' not in cache
    cache.remove_value(u'hiŏ')
    assert u'hiŏ' not in cache

def test_multi_keys():
    cache = Cache('newtests', data_dir='./cache', type='dbm')
    cache.clear()
    called = {}
    def create_func():
        called['here'] = True
        return 'howdy'
    
    try:
        cache.get_value('key1')
    except KeyError:
        pass
    else:
        raise Exception("Failed to keyerror on nonexistent key")

    assert 'howdy' == cache.get_value('key2', createfunc=create_func)
    assert called['here'] == True
    del called['here']

    try:
        cache.get_value('key3')
    except KeyError:
        pass
    else:
        raise Exception("Failed to keyerror on nonexistent key")
    try:
        cache.get_value('key1')
    except KeyError:
        pass
    else:
        raise Exception("Failed to keyerror on nonexistent key")
    
    assert 'howdy' == cache.get_value('key2', createfunc=create_func)
    assert called == {}

def test_increment():
    app = TestApp(CacheMiddleware(simple_app))
    res = app.get('/', extra_environ={'beaker.type':type, 'beaker.clear':True})
    assert 'current value is: 1' in res
    res = app.get('/')
    assert 'current value is: 2' in res
    res = app.get('/')
    assert 'current value is: 3' in res

def test_cache_manager():
    app = TestApp(CacheMiddleware(cache_manager_app))
    res = app.get('/')
    assert 'test_key is: test value' in res
    assert 'test_key cleared' in res
    
