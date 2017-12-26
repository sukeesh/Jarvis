import pytest
from sqlobject import SQLObject, SQLObjectNotFound, StringCol
from sqlobject.tests.dbtest import raises, setupClass, supports


########################################
# Transaction test
########################################


try:
    support_transactions = supports('transactions')
except NameError:
    # The module was imported during documentation building
    pass
else:
    if not support_transactions:
        pytestmark = pytest.mark.skip('')


class SOTestSOTrans(SQLObject):
    class sqlmeta:
        defaultOrder = 'name'
    name = StringCol(length=10, alternateID=True, dbName='name_col')


def test_transaction():
    setupClass(SOTestSOTrans)
    SOTestSOTrans(name='bob')
    SOTestSOTrans(name='tim')
    trans = SOTestSOTrans._connection.transaction()
    try:
        SOTestSOTrans._connection.autoCommit = 'exception'
        SOTestSOTrans(name='joe', connection=trans)
        trans.rollback()
        trans.begin()
        assert ([n.name for n in SOTestSOTrans.select(connection=trans)] ==
                ['bob', 'tim'])
        b = SOTestSOTrans.byName('bob', connection=trans)
        b.name = 'robert'
        trans.commit()
        assert b.name == 'robert'
        b.name = 'bob'
        trans.rollback()
        trans.begin()
        assert b.name == 'robert'
    finally:
        SOTestSOTrans._connection.autoCommit = True


def test_transaction_commit_sync():
    setupClass(SOTestSOTrans)
    connection = SOTestSOTrans._connection
    trans = connection.transaction()
    try:
        SOTestSOTrans(name='bob')
        bOut = SOTestSOTrans.byName('bob')
        bIn = SOTestSOTrans.byName('bob', connection=trans)
        bIn.name = 'robert'
        assert bOut.name == 'bob'
        trans.commit()
        assert bOut.name == 'robert'
    finally:
        trans.rollback()
        connection.autoCommit = True
        connection.close()


def test_transaction_delete(close=False):
    setupClass(SOTestSOTrans)
    connection = SOTestSOTrans._connection
    if (connection.dbName == 'sqlite') and connection._memory:
        pytest.skip("The test doesn't work with sqlite memory connection")
    trans = connection.transaction()
    try:
        SOTestSOTrans(name='bob')
        bIn = SOTestSOTrans.byName('bob', connection=trans)
        bIn.destroySelf()
        bOut = SOTestSOTrans.select(SOTestSOTrans.q.name == 'bob')
        assert bOut.count() == 1
        bOutInst = bOut[0]
        bOutID = bOutInst.id  # noqa: bOutID is used in the string code below
        trans.commit(close=close)
        assert bOut.count() == 0
        raises(SQLObjectNotFound, "SOTestSOTrans.get(bOutID)")
        raises(SQLObjectNotFound, "bOutInst.name")
    finally:
        trans.rollback()
        connection.autoCommit = True
        connection.close()


def test_transaction_delete_with_close():
    test_transaction_delete(close=True)
