from sqlobject import EnumCol, SQLObject, UnicodeCol
from sqlobject.col import validators
from sqlobject.tests.dbtest import raises, setupClass


########################################
# Enum test
########################################


class Enum1(SQLObject):

    cl = EnumCol(enumValues=['a', 'bcd', 'e'])


def testBad():
    setupClass(Enum1)
    for _l in ['a', 'bcd', 'a', 'e']:
        Enum1(cl=_l)
    raises(
        (Enum1._connection.module.IntegrityError,
         Enum1._connection.module.ProgrammingError,
         validators.Invalid),
        Enum1, cl='b')


class EnumWithNone(SQLObject):

    cl = EnumCol(enumValues=['a', 'bcd', 'e', None])


def testNone():
    setupClass(EnumWithNone)
    for _l in [None, 'a', 'bcd', 'a', 'e', None]:
        e = EnumWithNone(cl=_l)
        assert e.cl == _l


class EnumWithDefaultNone(SQLObject):

    cl = EnumCol(enumValues=['a', 'bcd', 'e', None], default=None)


def testDefaultNone():
    setupClass(EnumWithDefaultNone)

    e = EnumWithDefaultNone()
    assert e.cl is None


class EnumWithDefaultOther(SQLObject):

    cl = EnumCol(enumValues=['a', 'bcd', 'e', None], default='a')


def testDefaultOther():
    setupClass(EnumWithDefaultOther)

    e = EnumWithDefaultOther()
    assert e.cl == 'a'


class EnumUnicode(SQLObject):

    n = UnicodeCol()
    cl = EnumCol(enumValues=['a', 'b'])


def testUnicode():
    setupClass(EnumUnicode)

    EnumUnicode(n=u'a', cl='a')
    EnumUnicode(n=u'b', cl=u'b')
    EnumUnicode(n=u'\u201c', cl='a')
    EnumUnicode(n=u'\u201c', cl=u'b')
