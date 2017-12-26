from sqlobject import OR, RelatedJoin, SQLObject, StringCol, cache
from sqlobject.tests.dbtest import setupClass
from .test_basic import SOTestSO1, setupGetters


########################################
# Delete during select
########################################


def testSelect():
    setupGetters(SOTestSO1)
    for obj in SOTestSO1.select('all'):
        obj.destroySelf()
    assert list(SOTestSO1.select('all')) == []


########################################
# Delete many rows at once
########################################


def testDeleteMany():
    setupGetters(SOTestSO1)
    SOTestSO1.deleteMany(OR(SOTestSO1.q.name == "bob",
                            SOTestSO1.q.name == "fred"))
    assert len(list(SOTestSO1.select('all'))) == 2


def testDeleteBy():
    setupGetters(SOTestSO1)
    SOTestSO1.deleteBy(name="dave")
    assert len(list(SOTestSO1.select())) == 3


########################################
# Delete without caching
########################################


class NoCache(SQLObject):
    name = StringCol()


def testDestroySelf():
    setupClass(NoCache)
    old = NoCache._connection.cache
    NoCache._connection.cache = cache.CacheSet(cache=False)
    value = NoCache(name='test')
    value.destroySelf()
    NoCache._connection.cache = old


########################################
# Delete from related joins
########################################


class Service(SQLObject):
    groups = RelatedJoin("ServiceGroup")


class ServiceGroup(SQLObject):
    services = RelatedJoin("Service")


def testDeleteRelatedJoins():
    setupClass([Service, ServiceGroup])
    service = Service()
    service_group = ServiceGroup()
    service.addServiceGroup(service_group)
    service.destroySelf()
    service_group = ServiceGroup.get(service_group.id)
    assert len(service_group.services) == 0
