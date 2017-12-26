import pytest
from sqlobject import SQLObject
from sqlobject.tests.dbtest import setupClass, supports


class EmptyClass(SQLObject):

    pass


def test_empty():
    if not supports('emptyTable'):
        pytest.skip("emptyTable isn't supported")
    setupClass(EmptyClass)
    e1 = EmptyClass()
    e2 = EmptyClass()
    assert e1 != e2
    assert e1.id != e2.id
    assert e1 in list(EmptyClass.select())
    assert e2 in list(EmptyClass.select())
    e1.destroySelf()
    assert list(EmptyClass.select()) == [e2]
