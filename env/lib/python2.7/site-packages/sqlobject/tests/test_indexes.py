import pytest
from sqlobject import DatabaseIndex, ForeignKey, IntCol, MultipleJoin, \
    SQLObject, StringCol
from sqlobject.dberrors import DatabaseError, IntegrityError, \
    OperationalError, ProgrammingError
from sqlobject.tests.dbtest import raises, setupClass, supports


########################################
# Indexes
########################################


class SOIndex1(SQLObject):
    name = StringCol(length=100)
    number = IntCol()

    nameIndex = DatabaseIndex('name', unique=True)
    nameIndex2 = DatabaseIndex(name, number)
    nameIndex3 = DatabaseIndex({'column': name,
                                'length': 3})


class SOIndex2(SQLObject):
    name = StringCol(length=100)
    nameIndex = DatabaseIndex({'expression': 'lower(name)'})


def test_indexes_1():
    setupClass(SOIndex1)
    n = 0
    for name in 'blah blech boring yep yort snort'.split():
        n += 1
        SOIndex1(name=name, number=n)
    mod = SOIndex1._connection.module
    raises(
        (mod.ProgrammingError, mod.IntegrityError,
         mod.OperationalError, mod.DatabaseError,
         ProgrammingError, IntegrityError, OperationalError, DatabaseError),
        SOIndex1, name='blah', number=0)


def test_indexes_2():
    if not supports('expressionIndex'):
        pytest.skip("expressionIndex isn't supported")
    setupClass(SOIndex2)
    SOIndex2(name='')


class PersonIndexGet(SQLObject):
    firstName = StringCol(length=100)
    lastName = StringCol(length=100)
    age = IntCol(alternateID=True)
    nameIndex = DatabaseIndex(firstName, lastName, unique=True)


def test_index_get_1():
    setupClass(PersonIndexGet, force=True)

    PersonIndexGet(firstName='Eric', lastName='Idle', age=62)
    PersonIndexGet(firstName='Terry', lastName='Gilliam', age=65)
    PersonIndexGet(firstName='John', lastName='Cleese', age=66)

    PersonIndexGet.get(1)
    PersonIndexGet.nameIndex.get('Terry', 'Gilliam')
    PersonIndexGet.nameIndex.get(firstName='John', lastName='Cleese')

    raises(Exception, PersonIndexGet.nameIndex.get,
           firstName='Graham', lastName='Chapman')

    raises(Exception, PersonIndexGet.nameIndex.get,
           'Terry', lastName='Gilliam')

    raises(Exception, PersonIndexGet.nameIndex.get, 'Terry', 'Gilliam', 65)

    raises(Exception, PersonIndexGet.nameIndex.get, 'Terry')


class PersonIndexGet2(SQLObject):
    name = StringCol(alternateID=True, length=100)
    age = IntCol()
    addresses = MultipleJoin('AddressIndexGet2')


class AddressIndexGet2(SQLObject):
    person = ForeignKey('PersonIndexGet2', notNone=True)
    type = StringCol(notNone=True, length=100)
    street = StringCol(notNone=True)
    pk = DatabaseIndex(person, type, unique=True)


def test_index_get_2():
    setupClass([PersonIndexGet2, AddressIndexGet2])

    p = PersonIndexGet2(name='Terry Guilliam', age=64)
    AddressIndexGet2(person=p, type='home', street='Terry Street 234')
    AddressIndexGet2(person=p, type='work', street='Guilliam Street 234')

    AddressIndexGet2.pk.get(p, 'work')
    AddressIndexGet2.pk.get(person=p, type='work')
