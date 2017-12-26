from sqlobject import ForeignKey, IntCol, SQLObject
from sqlobject.tests.dbtest import setupClass


########################################
# Distinct
########################################


class Distinct1(SQLObject):
    n = IntCol()


class Distinct2(SQLObject):
    other = ForeignKey('Distinct1')


def count(select):
    result = {}
    for ob in select:
        result[int(ob.n)] = result.get(int(ob.n), 0) + 1
    return result


def test_distinct():
    setupClass([Distinct1, Distinct2])
    obs = [Distinct1(n=i) for i in range(3)]
    Distinct2(other=obs[0])
    Distinct2(other=obs[0])
    Distinct2(other=obs[1])

    query = (Distinct2.q.otherID == Distinct1.q.id)
    sel = Distinct1.select(query)
    assert count(sel) == {0: 2, 1: 1}
    sel = Distinct1.select(query, distinct=True)
    assert count(sel) == {0: 1, 1: 1}
