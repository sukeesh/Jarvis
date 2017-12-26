from sqlobject import SQLObject, StringCol
from sqlobject.sqlbuilder import JOIN, LEFTJOIN, LEFTJOINConditional, \
    LEFTJOINOn, LEFTJOINUsing
from sqlobject.tests.dbtest import getConnection, setupClass


########################################
# Condiotional joins
########################################


class SOTestJoin1(SQLObject):
    col1 = StringCol()


class SOTestJoin2(SQLObject):
    col2 = StringCol()


class SOTestJoin3(SQLObject):
    col3 = StringCol()


class SOTestJoin4(SQLObject):
    col4 = StringCol()


class SOTestJoin5(SQLObject):
    col5 = StringCol()


def setup():
    setupClass(SOTestJoin1)
    setupClass(SOTestJoin2)


def test_1syntax():
    setup()
    join = JOIN("table1", "table2")
    assert str(join) == "table1 JOIN table2"
    join = LEFTJOIN("table1", "table2")
    assert str(join) == "table1 LEFT JOIN table2"
    join = LEFTJOINOn("table1", "table2", "tabl1.col1 = table2.col2")
    assert getConnection().sqlrepr(join) == \
        "table1 LEFT JOIN table2 ON tabl1.col1 = table2.col2"


def test_2select_syntax():
    setup()
    select = SOTestJoin1.select(
        join=LEFTJOINConditional(SOTestJoin1, SOTestJoin2,
                                 on_condition=(
                                     SOTestJoin1.q.col1 == SOTestJoin2.q.col2))
    )
    assert str(select) == \
        "SELECT so_test_join1.id, so_test_join1.col1 " \
        "FROM so_test_join1 " \
        "LEFT JOIN so_test_join2 " \
        "ON ((so_test_join1.col1) = (so_test_join2.col2)) WHERE 1 = 1"


def test_3perform_join():
    setup()
    SOTestJoin1(col1="test1")
    SOTestJoin1(col1="test2")
    SOTestJoin1(col1="test3")
    SOTestJoin2(col2="test1")
    SOTestJoin2(col2="test2")

    select = SOTestJoin1.select(
        join=LEFTJOINOn(SOTestJoin1, SOTestJoin2,
                        SOTestJoin1.q.col1 == SOTestJoin2.q.col2)
    )
    assert select.count() == 3


def test_4join_3tables_syntax():
    setup()
    setupClass(SOTestJoin3)

    select = SOTestJoin1.select(
        join=LEFTJOIN(SOTestJoin2, SOTestJoin3)
    )
    assert str(select) == \
        "SELECT so_test_join1.id, so_test_join1.col1 " \
        "FROM so_test_join1, so_test_join2 LEFT JOIN so_test_join3 WHERE 1 = 1"


def test_5join_3tables_syntax2():
    setup()
    setupClass(SOTestJoin3)

    select = SOTestJoin1.select(
        join=(LEFTJOIN(None, SOTestJoin2), LEFTJOIN(None, SOTestJoin3))
    )
    assert str(select) == \
        "SELECT so_test_join1.id, so_test_join1.col1 " \
        "FROM so_test_join1  " \
        "LEFT JOIN so_test_join2  LEFT JOIN so_test_join3 WHERE 1 = 1"

    select = SOTestJoin1.select(
        join=(LEFTJOIN(SOTestJoin1, SOTestJoin2),
              LEFTJOIN(SOTestJoin1, SOTestJoin3))
    )
    assert str(select) == \
        "SELECT so_test_join1.id, so_test_join1.col1 " \
        "FROM so_test_join1 " \
        "LEFT JOIN so_test_join2, so_test_join1 " \
        "LEFT JOIN so_test_join3 WHERE 1 = 1"


def test_6join_using():
    setup()
    setupClass(SOTestJoin3)

    select = SOTestJoin1.select(
        join=LEFTJOINUsing(None, SOTestJoin2, [SOTestJoin2.q.id])
    )
    assert str(select) == \
        "SELECT so_test_join1.id, so_test_join1.col1 " \
        "FROM so_test_join1 " \
        "LEFT JOIN so_test_join2 USING (so_test_join2.id) WHERE 1 = 1"


def test_7join_on():
    setup()
    setupClass(SOTestJoin3)
    setupClass(SOTestJoin4)
    setupClass(SOTestJoin5)

    select = SOTestJoin1.select(join=(
        LEFTJOINOn(SOTestJoin2, SOTestJoin3,
                   SOTestJoin2.q.col2 == SOTestJoin3.q.col3),
        LEFTJOINOn(SOTestJoin4, SOTestJoin5,
                   SOTestJoin4.q.col4 == SOTestJoin5.q.col5)
    ))
    assert str(select) == \
        "SELECT so_test_join1.id, so_test_join1.col1 " \
        "FROM so_test_join1, so_test_join2 " \
        "LEFT JOIN so_test_join3 " \
        "ON ((so_test_join2.col2) = (so_test_join3.col3)), so_test_join4 " \
        "LEFT JOIN so_test_join5 " \
        "ON ((so_test_join4.col4) = (so_test_join5.col5)) WHERE 1 = 1"
