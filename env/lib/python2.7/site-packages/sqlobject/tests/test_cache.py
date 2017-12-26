from sqlobject import SQLObject, StringCol
from sqlobject.cache import CacheSet
from .dbtest import setupClass


class Something(object):
    pass


def test_purge1():
    x = CacheSet()
    y = Something()
    obj = x.get(1, y.__class__)
    assert obj is None
    x.put(1, y.__class__, y)
    x.finishPut(y.__class__)
    j = x.get(1, y.__class__)
    assert j == y
    x.expire(1, y.__class__)
    j = x.get(1, y.__class__)
    assert j is None
    x.finishPut(y.__class__)
    j = x.get(1, y.__class__)
    assert j is None
    x.finishPut(y.__class__)


class CacheTest(SQLObject):
    name = StringCol(alternateID=True, length=100)


def test_cache():
    setupClass(CacheTest)
    s = CacheTest(name='foo')
    obj_id = id(s)
    s_id = s.id
    assert CacheTest.get(s_id) is s
    assert not s.sqlmeta.expired
    CacheTest.sqlmeta.expireAll()
    assert s.sqlmeta.expired
    CacheTest.sqlmeta.expireAll()
    s1 = CacheTest.get(s_id)
    # We should have a new object:
    assert id(s1) != obj_id
    obj_id2 = id(s1)
    CacheTest._connection.expireAll()
    s2 = CacheTest.get(s_id)
    assert id(s2) != obj_id and id(s2) != obj_id2


def test_cache_cull():
    setupClass(CacheTest)
    s = CacheTest(name='test_cache_create')
    for count in range(s._connection.cache.caches['CacheTest'].cullFrequency):
        CacheTest(name='test_cache_create %d' % count)
    assert len(s._connection.cache.caches['CacheTest'].cache) < \
        s._connection.cache.caches['CacheTest'].cullFrequency
