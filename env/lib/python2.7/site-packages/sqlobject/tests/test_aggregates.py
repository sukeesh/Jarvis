from sqlobject import FloatCol, IntCol, SQLObject
from sqlobject.tests.dbtest import setupClass


# Test MIN, AVG, MAX, COUNT, SUM


class IntAccumulator(SQLObject):
    so_value = IntCol()


class FloatAccumulator(SQLObject):
    so_value = FloatCol()


def test_integer():
    setupClass(IntAccumulator)
    IntAccumulator(so_value=1)
    IntAccumulator(so_value=2)
    IntAccumulator(so_value=3)

    assert IntAccumulator.select().min(IntAccumulator.q.so_value) == 1
    assert IntAccumulator.select().avg(IntAccumulator.q.so_value) == 2
    assert IntAccumulator.select().max(IntAccumulator.q.so_value) == 3
    assert IntAccumulator.select().sum(IntAccumulator.q.so_value) == 6

    assert IntAccumulator.select(IntAccumulator.q.so_value > 1).\
        max(IntAccumulator.q.so_value) == 3
    assert IntAccumulator.select(IntAccumulator.q.so_value > 1).\
        sum(IntAccumulator.q.so_value) == 5


def floatcmp(f1, f2):
    if abs(f1 - f2) < 0.1:
        return 0
    if f1 < f2:
        return 1
    return -1


def test_float():
    setupClass(FloatAccumulator)
    FloatAccumulator(so_value=1.2)
    FloatAccumulator(so_value=2.4)
    FloatAccumulator(so_value=3.8)

    assert floatcmp(
        FloatAccumulator.select().min(FloatAccumulator.q.so_value), 1.2) == 0
    assert floatcmp(
        FloatAccumulator.select().avg(FloatAccumulator.q.so_value), 2.5) == 0
    assert floatcmp(
        FloatAccumulator.select().max(FloatAccumulator.q.so_value), 3.8) == 0
    assert floatcmp(
        FloatAccumulator.select().sum(FloatAccumulator.q.so_value), 7.4) == 0


def test_many():
    setupClass(IntAccumulator)
    IntAccumulator(so_value=1)
    IntAccumulator(so_value=1)
    IntAccumulator(so_value=2)
    IntAccumulator(so_value=2)
    IntAccumulator(so_value=3)
    IntAccumulator(so_value=3)

    attribute = IntAccumulator.q.so_value
    assert list(IntAccumulator.select().accumulateMany(
        ("MIN", attribute), ("AVG", attribute), ("MAX", attribute),
        ("COUNT", attribute), ("SUM", attribute)
    )) == [1, 2, 3, 6, 12]

    assert list(IntAccumulator.select(distinct=True).accumulateMany(
        ("MIN", attribute), ("AVG", attribute), ("MAX", attribute),
        ("COUNT", attribute), ("SUM", attribute)
    )) == [1, 2, 3, 3, 6]
