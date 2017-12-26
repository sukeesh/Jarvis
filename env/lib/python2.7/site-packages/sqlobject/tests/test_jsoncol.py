from sqlobject import SQLObject, JSONCol
from sqlobject.tests.dbtest import setupClass


class JSONTest(SQLObject):
    json = JSONCol(default=None)


_json_test_data = (
    None, True, 1, 2.0,
    {u"test": [None, True, 1, 2.0,
     {u"unicode'with'apostrophes": u"unicode\"with\"quotes"},
     [],
     u"unicode"]},
    [None, True, 1, 2.0,
     [],
     {u"unicode'with'apostrophes": u"unicode\"with\"quotes"},
     u"unicode", u"unicode'with'apostrophes", u"unicode\"with\"quotes",
     ],
    u"unicode", u"unicode'with'apostrophes", u"unicode\"with\"quotes",
)


def test_JSONCol():
    setupClass(JSONTest)

    for _id, test_data in enumerate(_json_test_data):
        json = JSONTest(id=_id + 1, json=test_data)

    JSONTest._connection.cache.clear()

    for _id, test_data in enumerate(_json_test_data):
        json = JSONTest.get(_id + 1)
        assert json.json == test_data
