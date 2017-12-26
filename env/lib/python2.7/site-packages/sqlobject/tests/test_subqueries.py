from sqlobject import ForeignKey, SQLObject, StringCol
from sqlobject.sqlbuilder import EXISTS, IN, LEFTOUTERJOINOn, NOTEXISTS, \
    Outer, Select
from sqlobject.tests.dbtest import setupClass


########################################
# Subqueries (subselects)
########################################


class SOTestIn1(SQLObject):
    col1 = StringCol()


class SOTestIn2(SQLObject):
    col2 = StringCol()


class SOTestOuter(SQLObject):
    fk = ForeignKey('SOTestIn1')


def setup():
    setupClass(SOTestIn1)
    setupClass(SOTestIn2)


def insert():
    setup()
    SOTestIn1(col1=None)
    SOTestIn1(col1='')
    SOTestIn1(col1="test")
    SOTestIn2(col2=None)
    SOTestIn2(col2='')
    SOTestIn2(col2="test")


def test_1syntax_in():
    setup()
    select = SOTestIn1.select(IN(SOTestIn1.q.col1, Select(SOTestIn2.q.col2)))
    assert str(select) == \
        "SELECT so_test_in1.id, so_test_in1.col1 " \
        "FROM so_test_in1 WHERE so_test_in1.col1 IN " \
        "(SELECT so_test_in2.col2 FROM so_test_in2)"

    select = SOTestIn1.select(IN(SOTestIn1.q.col1, SOTestIn2.select()))
    assert str(select) == \
        "SELECT so_test_in1.id, so_test_in1.col1 " \
        "FROM so_test_in1 WHERE so_test_in1.col1 IN " \
        "(SELECT so_test_in2.id FROM so_test_in2 WHERE 1 = 1)"


def test_2perform_in():
    insert()
    select = SOTestIn1.select(IN(SOTestIn1.q.col1, Select(SOTestIn2.q.col2)))
    assert select.count() == 2


def test_3syntax_exists():
    setup()
    select = SOTestIn1.select(NOTEXISTS(
        Select(SOTestIn2.q.col2,
               where=(Outer(SOTestIn1).q.col1 == SOTestIn2.q.col2))))
    assert str(select) == \
        "SELECT so_test_in1.id, so_test_in1.col1 " \
        "FROM so_test_in1 WHERE NOT EXISTS " \
        "(SELECT so_test_in2.col2 FROM so_test_in2 " \
        "WHERE ((so_test_in1.col1) = (so_test_in2.col2)))"

    setupClass(SOTestOuter)
    select = SOTestOuter.select(NOTEXISTS(
        Select(SOTestIn1.q.col1,
               where=(Outer(SOTestOuter).q.fk == SOTestIn1.q.id))))
    assert str(select) == \
        "SELECT so_test_outer.id, so_test_outer.fk_id " \
        "FROM so_test_outer WHERE NOT EXISTS " \
        "(SELECT so_test_in1.col1 FROM so_test_in1 " \
        "WHERE ((so_test_outer.fk_id) = (so_test_in1.id)))"


def test_4perform_exists():
    insert()
    select = SOTestIn1.select(EXISTS(
        Select(SOTestIn2.q.col2,
               where=(Outer(SOTestIn1).q.col1 == SOTestIn2.q.col2))))
    assert len(list(select)) == 2

    setupClass(SOTestOuter)
    select = SOTestOuter.select(NOTEXISTS(
        Select(SOTestIn1.q.col1,
               where=(Outer(SOTestOuter).q.fkID == SOTestIn1.q.id))))
    assert len(list(select)) == 0


def test_4syntax_direct():
    setup()
    select = SOTestIn1.select(SOTestIn1.q.col1 == Select(SOTestIn2.q.col2,
                              where=(SOTestIn2.q.col2 == "test")))
    assert str(select) == \
        "SELECT so_test_in1.id, so_test_in1.col1 " \
        "FROM so_test_in1 WHERE ((so_test_in1.col1) = " \
        "(SELECT so_test_in2.col2 FROM so_test_in2 " \
        "WHERE ((so_test_in2.col2) = ('test'))))"


def test_4perform_direct():
    insert()
    select = SOTestIn1.select(SOTestIn1.q.col1 == Select(SOTestIn2.q.col2,
                              where=(SOTestIn2.q.col2 == "test")))
    assert select.count() == 1


def test_5perform_direct():
    insert()
    select = SOTestIn1.select(SOTestIn1.q.col1 == Select(SOTestIn2.q.col2,
                              where=(SOTestIn2.q.col2 == "test")))
    assert select.count() == 1


def test_6syntax_join():
    insert()
    j = LEFTOUTERJOINOn(SOTestIn2, SOTestIn1,
                        SOTestIn1.q.col1 == SOTestIn2.q.col2)
    select = SOTestIn1.select(SOTestIn1.q.col1 == Select(SOTestIn2.q.col2,
                              where=(SOTestIn2.q.col2 == "test"), join=j))
    assert str(select) == \
        "SELECT so_test_in1.id, so_test_in1.col1 " \
        "FROM so_test_in1 WHERE ((so_test_in1.col1) = " \
        "(SELECT so_test_in2.col2 FROM so_test_in2 " \
        "LEFT OUTER JOIN so_test_in1 ON " \
        "((so_test_in1.col1) = (so_test_in2.col2)) " \
        "WHERE ((so_test_in2.col2) = ('test'))))"


def test_6perform_join():
    insert()
    j = LEFTOUTERJOINOn(SOTestIn2, SOTestIn1,
                        SOTestIn1.q.col1 == SOTestIn2.q.col2)
    select = SOTestIn1.select(SOTestIn1.q.col1 == Select(SOTestIn2.q.col2,
                              where=(SOTestIn2.q.col2 == "test"), join=j))
    assert select.count() == 1
