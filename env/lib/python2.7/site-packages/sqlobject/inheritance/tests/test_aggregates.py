from sqlobject import IntCol
from sqlobject.inheritance import InheritableSQLObject
from sqlobject.tests.dbtest import raises, setupClass


class SOTestAggregate1(InheritableSQLObject):
    value1 = IntCol()


class SOTestAggregate2(SOTestAggregate1):
    value2 = IntCol()


def test_aggregates():
    setupClass([SOTestAggregate1, SOTestAggregate2])

    SOTestAggregate1(value1=1)
    SOTestAggregate2(value1=2, value2=12)

    assert SOTestAggregate1.select().max("value1") == 2
    assert SOTestAggregate2.select().max("value1") == 2
    raises(Exception, SOTestAggregate2.select().max, "value2")
    assert SOTestAggregate2.select().max(SOTestAggregate2.q.value2) == 12
