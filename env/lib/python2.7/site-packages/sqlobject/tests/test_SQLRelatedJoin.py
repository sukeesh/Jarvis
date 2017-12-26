import pytest
from sqlobject import RelatedJoin, SQLObject, SQLRelatedJoin, StringCol
from sqlobject.tests.dbtest import setupClass, supports


class Fighter(SQLObject):
    class sqlmeta:
        idName = 'fighter_id'  # test on a non-standard way
    name = StringCol()
    tourtments = RelatedJoin('Tourtment')


class Tourtment(SQLObject):
    class sqlmeta:
        table = 'competition'  # test on a non-standard way
    name = StringCol()
    fightersAsList = RelatedJoin('Fighter')
    fightersAsSResult = SQLRelatedJoin('Fighter')


def createAllTables():
    setupClass(Fighter)
    setupClass(Tourtment)


def test_1():
    createAllTables()
    # create some tourtments
    t1 = Tourtment(name='Tourtment #1')
    t2 = Tourtment(name='Tourtment #2')
    t3 = Tourtment(name='Tourtment #3')
    # create some fighters
    gokou = Fighter(name='gokou')
    vegeta = Fighter(name='vegeta')
    gohan = Fighter(name='gohan')
    trunks = Fighter(name='trunks')
    # relating them
    t1.addFighter(gokou)
    t1.addFighter(vegeta)
    t1.addFighter(gohan)
    t2.addFighter(gokou)
    t2.addFighter(vegeta)
    t2.addFighter(trunks)
    t3.addFighter(gohan)
    t3.addFighter(trunks)
    # do some selects
    for i, j in zip(t1.fightersAsList, t1.fightersAsSResult):
        assert i is j
    assert len(t2.fightersAsList) == t2.fightersAsSResult.count()


def test_related_join_transaction():
    if not supports('transactions'):
        pytest.skip("Transactions aren't supported")
    createAllTables()
    trans = Tourtment._connection.transaction()
    try:
        t1 = Tourtment(name='Tourtment #1', connection=trans)
        t1.addFighter(Fighter(name='Jim', connection=trans))
        assert t1.fightersAsSResult.count() == 1
        assert t1.fightersAsSResult[0]._connection == trans
    finally:
        trans.commit(True)
        Tourtment._connection.autoCommit = True
