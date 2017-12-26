from sqlobject import SQLObject, StringCol
from sqlobject.tests.dbtest import setupClass


########################################
# Inheritance
########################################


class Super(SQLObject):

    name = StringCol(length=10)


class Sub(Super):

    name2 = StringCol(length=10)


def test_super():
    setupClass(Super)
    setupClass(Sub)
    s1 = Super(name='one')
    Super(name='two')  # s2
    s3 = Super.get(s1.id)
    assert s1 == s3


def test_sub():
    setupClass(Super)
    setupClass(Sub)
    s1 = Sub(name='one', name2='1')
    Sub(name='two', name2='2')  # s2
    s3 = Sub.get(s1.id)
    assert s1 == s3
