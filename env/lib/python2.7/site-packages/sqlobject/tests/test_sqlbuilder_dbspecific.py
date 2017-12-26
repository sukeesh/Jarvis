from __future__ import print_function

from sqlobject import BoolCol, SQLObject
from sqlobject.sqlbuilder import AND, Alias, EXISTS, JOIN, LEFTJOINOn, \
    Select, sqlrepr
from sqlobject.tests.dbtest import setupClass

''' Going to test that complex sqlbuilder constructions are never
    prematurely stringified. A straight-forward approach is to use
    Bools, since postgresql wants special formatting in queries.
    The test is whether a call to sqlrepr(x, 'postgres') includes
    the appropriate bool formatting throughout.
'''


class SBButton(SQLObject):
    activated = BoolCol()


def makeClause():
    # It's not a comparison, it's an SQLExpression
    return SBButton.q.activated == True  # noqa


def makeSelect():
    return Select(SBButton.q.id, clause=makeClause())


def checkCount(q, c, msg=''):
    print("STRING:", str(q))
    print("POSTGR:", sqlrepr(q, 'postgres'))
    assert sqlrepr(q, 'postgres').count("'t'") == c and \
        sqlrepr(q, 'postgres') != str(q), msg


def testSimple():
    setupClass(SBButton)
    checkCount(makeClause(), 1)
    checkCount(makeSelect(), 1)


def testMiscOps():
    setupClass(SBButton)
    checkCount(AND(makeClause(), makeClause()), 2)
    checkCount(AND(makeClause(), EXISTS(makeSelect())), 2)


def testAliased():
    setupClass(SBButton)
    b = Alias(makeSelect(), 'b')
    checkCount(b, 1)
    checkCount(Select(b.q.id), 1)

    # Table1 & Table2 are treated individually in joins
    checkCount(JOIN(None, b), 1)
    checkCount(JOIN(b, SBButton), 1)
    checkCount(JOIN(SBButton, b), 1)
    checkCount(LEFTJOINOn(None, b, SBButton.q.id == b.q.id), 1)
    checkCount(LEFTJOINOn(b, SBButton, SBButton.q.id == b.q.id), 1)
    checkCount(LEFTJOINOn(SBButton, b, SBButton.q.id == b.q.id), 1)


def testTablesUsedSResults():
    setupClass(SBButton)

    checkCount(SBButton.select(makeClause()).queryForSelect(), 1)
