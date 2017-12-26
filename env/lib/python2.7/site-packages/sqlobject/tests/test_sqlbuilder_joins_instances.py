from sqlobject import AND, ForeignKey, SQLMultipleJoin, SQLObject, \
    SQLRelatedJoin, StringCol
from sqlobject.tests.dbtest import inserts, setupClass

# Testing for expressing join, foreign keys,
# and instance identity in SQLBuilder expressions.


class SBPerson(SQLObject):
    name = StringCol()
    addresses = SQLMultipleJoin('SBAddress', joinColumn='personID')
    sharedAddresses = SQLRelatedJoin('SBAddress',
                                     addRemoveName='SharedAddress')


class SBAddress(SQLObject):
    city = StringCol()
    person = ForeignKey('SBPerson')
    sharedPeople = SQLRelatedJoin('SBPerson')


def setup_module(mod):
    global ppl
    setupClass([SBPerson, SBAddress])
    ppl = inserts(SBPerson, [('James',), ('Julia',)], 'name')
    adds = inserts(SBAddress, [('London', ppl[0].id),
                               ('Chicago', ppl[1].id),
                               ('Abu Dhabi', ppl[1].id)],
                   'city personID')
    ppl[0].addSharedAddress(adds[0])
    ppl[0].addSharedAddress(adds[1])
    ppl[1].addSharedAddress(adds[0])


def testJoin():
    assert list(SBPerson.select(
        AND(SBPerson.q.id == SBAddress.q.personID,
            SBAddress.q.city == 'London'))) == \
        list(SBAddress.selectBy(city='London').throughTo.person)

    assert list(SBAddress.select(
        AND(SBPerson.q.id == SBAddress.q.personID,
            SBPerson.q.name == 'Julia')).orderBy(SBAddress.q.city)) == \
        list(SBPerson.selectBy(name='Julia').
             throughTo.addresses.orderBy(SBAddress.q.city))


def testRelatedJoin():
    assert list(SBPerson.selectBy(name='Julia').throughTo.sharedAddresses) == \
        list(ppl[1].sharedAddresses)


def testInstance():
    assert list(SBAddress.select(
        AND(SBPerson.q.id == SBAddress.q.personID, SBPerson.q.id == ppl[0].id)
    )) == list(ppl[0].addresses)


def testFK():
    assert list(SBPerson.select(
        AND(SBAddress.j.person, SBAddress.q.city == 'London'))) == \
        list(SBPerson.select(
            AND(SBPerson.q.id == SBAddress.q.personID,
                SBAddress.q.city == 'London')))


def testRelatedJoin2():
    assert list(SBAddress.select(
        AND(SBAddress.j.sharedPeople, SBPerson.q.name == 'Julia'))) == \
        list(SBPerson.select(
             SBPerson.q.name == 'Julia').throughTo.sharedAddresses)


def testJoin2():
    assert list(SBAddress.select(
        AND(SBPerson.j.addresses,
            SBPerson.q.name == 'Julia')).orderBy(SBAddress.q.city)) == \
        list(SBAddress.select(
            AND(SBPerson.q.id == SBAddress.q.personID,
                SBPerson.q.name == 'Julia')).orderBy(SBAddress.q.city)) == \
        list(SBPerson.selectBy(name='Julia').throughTo.
             addresses.orderBy(SBAddress.q.city))


def testFK2():
    assert list(SBAddress.select(
        AND(SBAddress.j.person, SBPerson.q.name == 'Julia'))) == \
        list(SBAddress.select(
            AND(SBPerson.q.id == SBAddress.q.personID,
                SBPerson.q.name == 'Julia')))
