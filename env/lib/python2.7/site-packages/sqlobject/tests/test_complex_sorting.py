from sqlobject import IntCol, SQLObject, StringCol, sqlmeta
from sqlobject.tests.dbtest import inserts, setupClass

# Test more complex orderBy clauses


class ComplexNames(SQLObject):

    class sqlmeta(sqlmeta):
        table = 'names_table'
        defaultOrder = ['lastName', 'firstName', 'phone', 'age']

    firstName = StringCol(length=30)
    lastName = StringCol(length=30)
    phone = StringCol(length=11)
    age = IntCol()


def setupComplexNames():
    setupClass(ComplexNames)
    inserts(ComplexNames, [('aj', 'baker', '555-444-333', 34),
                           ('joe', 'robbins', '444-555-333', 34),
                           ('tim', 'jackson', '555-444-222', 32),
                           ('joe', 'baker', '222-111-000', 24),
                           ('zoe', 'robbins', '444-555-333', 46)],
            schema='firstName lastName phone age')


def nameList(names):
    result = []
    for name in names:
        result.append('%s %s' % (name.firstName, name.lastName))
    return result


def firstList(names):
    return [n.firstName for n in names]


def test_defaultComplexOrder():
    setupComplexNames()
    assert nameList(ComplexNames.select()) == \
        ['aj baker', 'joe baker',
         'tim jackson', 'joe robbins',
         'zoe robbins']


def test_complexOrders():
    setupComplexNames()
    assert nameList(ComplexNames.select().orderBy(['age', 'phone',
                                                   'firstName',
                                                   'lastName'])) == \
        ['joe baker', 'tim jackson',
         'joe robbins', 'aj baker',
         'zoe robbins']
    assert nameList(ComplexNames.select().orderBy(['-age', 'phone',
                                                   'firstName',
                                                   'lastName'])) == \
        ['zoe robbins', 'joe robbins',
         'aj baker', 'tim jackson',
         'joe baker']
    assert nameList(ComplexNames.select().orderBy(['age', '-phone',
                                                   'firstName',
                                                   'lastName'])) == \
        ['joe baker', 'tim jackson',
         'aj baker', 'joe robbins',
         'zoe robbins']
    assert nameList(ComplexNames.select().orderBy(['-firstName', 'phone',
                                                   'lastName', 'age'])) == \
        ['zoe robbins', 'tim jackson',
         'joe baker', 'joe robbins',
         'aj baker']
    assert nameList(ComplexNames.select().orderBy(['-firstName', '-phone',
                                                   'lastName', 'age'])) == \
        ['zoe robbins', 'tim jackson',
         'joe robbins', 'joe baker',
         'aj baker']
