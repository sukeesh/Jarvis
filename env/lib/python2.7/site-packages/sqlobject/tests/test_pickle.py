import pickle
import pytest
from sqlobject import IntCol, SQLObject, StringCol
from sqlobject.tests.dbtest import getConnection, raises, setupClass


########################################
# Pickle instances
########################################


class SOTestPickle(SQLObject):
    question = StringCol()
    answer = IntCol()


test_question = 'The Ulimate Question of Life, the Universe and Everything'
test_answer = 42


def test_pickleCol():
    setupClass(SOTestPickle)
    connection = SOTestPickle._connection
    test = SOTestPickle(question=test_question, answer=test_answer)

    pickle_data = pickle.dumps(test, pickle.HIGHEST_PROTOCOL)
    connection.cache.clear()
    test = pickle.loads(pickle_data)
    test2 = connection.cache.tryGet(test.id, SOTestPickle)

    assert test2 is test
    assert test.question == test_question
    assert test.answer == test_answer

    if (connection.dbName == 'sqlite') and connection._memory:
        pytest.skip("The following test requires a different connection")

    test = SOTestPickle.get(
        test.id,
        # make a different DB URI and open another connection
        connection=getConnection(registry=''))
    raises(pickle.PicklingError, pickle.dumps, test, pickle.HIGHEST_PROTOCOL)
