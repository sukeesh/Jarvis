import pytest
from sqlobject import IntCol, SQLObject
from sqlobject.tests.dbtest import setupClass, supports


########################################
# Slicing tests
########################################


def listrange(*args):
    """Always return a list, for py3k compatibility"""
    return list(range(*args))


class Counter(SQLObject):

    number = IntCol(notNull=True)


class TestSlice:

    def setup_method(self, meth):
        setupClass(Counter)
        for i in range(100):
            Counter(number=i)

    def counterEqual(self, counters, value):
        if not supports('limitSelect'):
            pytest.skip("limitSelect isn't supported")
        assert [c.number for c in counters] == value

    def test_slice(self):
        self.counterEqual(
            Counter.select(None, orderBy='number'), listrange(100))

        self.counterEqual(
            Counter.select(None, orderBy='number')[10:20],
            listrange(10, 20))

        self.counterEqual(
            Counter.select(None, orderBy='number')[20:30][:5],
            listrange(20, 25))

        self.counterEqual(
            Counter.select(None, orderBy='number')[20:30][1:5],
            listrange(21, 25))

        self.counterEqual(
            Counter.select(None, orderBy='number')[:-10],
            listrange(0, 90))

        self.counterEqual(
            Counter.select(None, orderBy='number', reversed=True),
            listrange(99, -1, -1))

        self.counterEqual(
            Counter.select(None, orderBy='-number'),
            listrange(99, -1, -1))
