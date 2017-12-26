from __future__ import print_function

from sqlobject import IntCol, SQLObject, StringCol, events
from sqlobject.inheritance import InheritableSQLObject
from sqlobject.tests.dbtest import setupClass


class EventTester(SQLObject):
    name = StringCol()


def make_watcher():
    log = []

    def watch(*args):
        log.append(args)

    watch.log = log
    return watch


def make_listen(signal, cls=None):
    if cls is None:
        cls = EventTester
    watcher = make_watcher()
    events.listen(watcher, cls, signal)
    return watcher


def test_create():
    watcher = make_listen(events.ClassCreateSignal)

    class EventTesterSub1(EventTester):
        pass

    class EventTesterSub2(EventTesterSub1):
        pass

    assert len(watcher.log) == 2
    assert len(watcher.log[0]) == 5
    assert watcher.log[0][0] == 'EventTesterSub1'
    assert watcher.log[0][1] == (EventTester,)
    assert isinstance(watcher.log[0][2], dict)
    assert isinstance(watcher.log[0][3], list)


def test_row_create():
    setupClass(EventTester)
    watcher = make_listen(events.RowCreateSignal)
    row1 = EventTester(name='foo')
    row2 = EventTester(name='bar')
    assert len(watcher.log) == 2
    assert watcher.log == [
        (row1, {'name': 'foo'}, []),
        (row2, {'name': 'bar'}, [])]


def test_row_destroy():
    setupClass(EventTester)
    watcher = make_listen(events.RowDestroySignal)
    f = EventTester(name='foo')
    assert not watcher.log
    f.destroySelf()
    assert watcher.log == [(f, [])]


def test_row_destroyed():
    setupClass(EventTester)
    watcher = make_listen(events.RowDestroyedSignal)
    f = EventTester(name='foo')
    assert not watcher.log
    f.destroySelf()
    assert watcher.log == [(f, [])]


def test_row_update():
    setupClass(EventTester)
    watcher = make_listen(events.RowUpdateSignal)
    f = EventTester(name='bar')
    assert not watcher.log
    f.name = 'bar2'
    f.set(name='bar3')
    assert watcher.log == [
        (f, {'name': 'bar2'}),
        (f, {'name': 'bar3'})]


def test_row_updated():
    setupClass(EventTester)
    watcher = make_listen(events.RowUpdatedSignal)
    f = EventTester(name='bar')
    assert not watcher.log
    f.name = 'bar2'
    f.set(name='bar3')
    assert watcher.log == [(f, []), (f, [])]


def test_add_column():
    setupClass(EventTester)
    watcher = make_listen(events.AddColumnSignal)
    events.summarize_events_by_sender()

    class NewEventTester(EventTester):
        name2 = StringCol()

    expect = (
        NewEventTester, None,
        'name2', NewEventTester.sqlmeta.columnDefinitions['name2'],
        False, [])
    print(zip(watcher.log[1], expect))
    assert watcher.log[1] == expect


class InheritableEventTestA(InheritableSQLObject):
    a = IntCol()


class InheritableEventTestB(InheritableEventTestA):
    b = IntCol()


class InheritableEventTestC(InheritableEventTestB):
    c = IntCol()


def _query(instance):
    row = InheritableEventTestA.get(instance.id)
    assert isinstance(row, InheritableEventTestC)
    assert row.c == 3


def _signal(instance, kwargs, postfuncs):
    postfuncs.append(_query)


def test_inheritance_row_created():
    setupClass([InheritableEventTestA, InheritableEventTestB,
                InheritableEventTestC])

    events.listen(_signal, InheritableEventTestA, events.RowCreatedSignal)

    InheritableEventTestC(a=1, b=2, c=3)
