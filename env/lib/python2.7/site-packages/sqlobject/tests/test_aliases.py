from sqlobject import SQLObject, StringCol
from sqlobject.sqlbuilder import Alias, LEFTJOINOn
from sqlobject.tests.dbtest import setupClass


########################################
# Table aliases and self-joins
########################################


class JoinAlias(SQLObject):
    name = StringCol()
    parent = StringCol()


def test_1syntax():
    setupClass(JoinAlias)
    alias = Alias(JoinAlias)
    select = JoinAlias.select(JoinAlias.q.parent == alias.q.name)
    assert str(select) == \
        "SELECT join_alias.id, join_alias.name, join_alias.parent " \
        "FROM join_alias, join_alias  join_alias_alias1 " \
        "WHERE ((join_alias.parent) = (join_alias_alias1.name))"


def test_2perform_join():
    setupClass(JoinAlias)
    JoinAlias(name="grandparent", parent=None)
    JoinAlias(name="parent", parent="grandparent")
    JoinAlias(name="child", parent="parent")
    alias = Alias(JoinAlias)
    select = JoinAlias.select(JoinAlias.q.parent == alias.q.name)
    assert select.count() == 2


def test_3joins():
    setupClass(JoinAlias)
    alias = Alias(JoinAlias)
    select = JoinAlias.select(
        (JoinAlias.q.name == 'a') & (alias.q.name == 'b'),
        join=LEFTJOINOn(None, alias, alias.q.name == 'c')
    )
    assert str(select) == \
        "SELECT join_alias.id, join_alias.name, join_alias.parent " \
        "FROM join_alias " \
        "LEFT JOIN join_alias  join_alias_alias3 " \
        "ON ((join_alias_alias3.name) = ('c')) " \
        "WHERE (((join_alias.name) = ('a')) AND " \
        "((join_alias_alias3.name) = ('b')))"
