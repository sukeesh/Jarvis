# Test that selectResults handle NULL values from, for example, outer joins.

from sqlobject import ForeignKey, SQLObject, StringCol, sqlbuilder
from sqlobject.tests.dbtest import setupClass


class SOTestComposer(SQLObject):
    name = StringCol()


class SOTestWork(SQLObject):
    class sqlmeta:
        idName = "work_id"

    composer = ForeignKey('SOTestComposer')
    title = StringCol()


def test1():
    setupClass([SOTestComposer,
                SOTestWork])

    c = SOTestComposer(name='Mahler, Gustav')
    w = SOTestWork(composer=c, title='Symphony No. 9')
    SOTestComposer(name='Bruckner, Anton')
    # but don't add any works for Bruckner

    # do a left join, a common use case that often involves NULL results
    s = SOTestWork.select(
        join=sqlbuilder.LEFTJOINOn(
            SOTestComposer, SOTestWork,
            SOTestComposer.q.id == SOTestWork.q.composerID))
    assert tuple(s) == (w, None)
