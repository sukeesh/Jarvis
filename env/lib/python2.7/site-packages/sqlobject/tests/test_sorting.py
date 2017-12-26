from sqlobject import DESC, SQLObject, StringCol, sqlmeta
from sqlobject.tests.dbtest import inserts, setupClass


class Names(SQLObject):

    class sqlmeta(sqlmeta):
        table = 'names_table'
        defaultOrder = ['lastName', 'firstName']

    firstName = StringCol(length=30)
    lastName = StringCol(length=30)


def setupNames():
    setupClass(Names)
    inserts(Names, [('aj', 'baker'), ('joe', 'robbins'),
                    ('tim', 'jackson'), ('joe', 'baker'),
                    ('zoe', 'robbins')],
            schema='firstName lastName')


def nameList(names):
    result = []
    for name in names:
        result.append('%s %s' % (name.firstName, name.lastName))
    return result


def firstList(names):
    return [n.firstName for n in names]


def test_defaultOrder():
    setupNames()
    assert nameList(Names.select()) == \
        ['aj baker', 'joe baker',
         'tim jackson', 'joe robbins',
         'zoe robbins']


def test_otherOrder():
    setupNames()
    assert nameList(Names.select().orderBy(['firstName', 'lastName'])) == \
        ['aj baker', 'joe baker',
         'joe robbins', 'tim jackson',
         'zoe robbins']


def test_untranslatedColumnOrder():
    setupNames()
    assert nameList(Names.select().orderBy(['first_name', 'last_name'])) == \
        ['aj baker', 'joe baker',
         'joe robbins', 'tim jackson',
         'zoe robbins']


def test_singleUntranslatedColumnOrder():
    setupNames()
    assert firstList(Names.select().orderBy('firstName')) == \
        ['aj', 'joe', 'joe', 'tim', 'zoe']
    assert firstList(Names.select().orderBy('first_name')) == \
        ['aj', 'joe', 'joe', 'tim', 'zoe']
    assert firstList(Names.select().orderBy('-firstName')) == \
        ['zoe', 'tim', 'joe', 'joe', 'aj']
    assert firstList(Names.select().orderBy(u'-first_name')) == \
        ['zoe', 'tim', 'joe', 'joe', 'aj']
    assert firstList(Names.select().orderBy(Names.q.firstName)) == \
        ['aj', 'joe', 'joe', 'tim', 'zoe']
    assert firstList(Names.select().orderBy('firstName').reversed()) == \
        ['zoe', 'tim', 'joe', 'joe', 'aj']
    assert firstList(Names.select().orderBy('-firstName').reversed()) == \
        ['aj', 'joe', 'joe', 'tim', 'zoe']
    assert firstList(Names.select().orderBy(DESC(Names.q.firstName))) == \
        ['zoe', 'tim', 'joe', 'joe', 'aj']
    assert firstList(Names.select().orderBy(Names.q.firstName).reversed()) == \
        ['zoe', 'tim', 'joe', 'joe', 'aj']
    assert firstList(
        Names.select().orderBy(DESC(Names.q.firstName)).reversed()) == \
        ['aj', 'joe', 'joe', 'tim', 'zoe']
