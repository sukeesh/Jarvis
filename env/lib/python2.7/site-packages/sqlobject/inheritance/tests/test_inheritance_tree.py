from sqlobject import StringCol
from sqlobject.inheritance import InheritableSQLObject
from sqlobject.tests.dbtest import setupClass

########################################
# Inheritance Tree
########################################


class Tree1(InheritableSQLObject):
    aprop = StringCol(length=10)


class Tree2(Tree1):
    bprop = StringCol(length=10)


class Tree3(Tree1):
    cprop = StringCol(length=10)


class Tree4(Tree2):
    dprop = StringCol(length=10)


class Tree5(Tree2):
    eprop = StringCol(length=10)


def test_tree():
    setupClass([Tree1, Tree2, Tree3, Tree4, Tree5])

    Tree1(aprop='t1')  # t1
    t2 = Tree2(aprop='t2', bprop='t2')
    Tree3(aprop='t3', cprop='t3')  # t3
    t4 = Tree4(aprop='t4', bprop='t4', dprop='t4')
    t5 = Tree5(aprop='t5', bprop='t5', eprop='t5')

    # find just the t5 out of childs from Tree2
    assert t5 == Tree1.select(Tree2.q.childName == 'Tree5')[0]

    # t2,t4,t5 are all subclasses of Tree1 with t1 childName of 'Tree2'
    assert list(Tree1.select(
        Tree1.q.childName == 'Tree2', orderBy="aprop")) == [t2, t4, t5]
