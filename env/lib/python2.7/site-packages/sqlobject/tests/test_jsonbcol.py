import pytest
from sqlobject import SQLObject, JsonbCol
from sqlobject.tests.dbtest import getConnection, setupClass


########################################
# Jsonb columns
########################################


class JsonbContainer(SQLObject):
    jsondata = JsonbCol(default=None)
    jsondata_none = JsonbCol(default=None)
    jsondata_list = JsonbCol(default=None)


dictdata = dict(
    ship=u'USS Voyager',
    number='NCC-74656',
    crew=['Cpt. Janeway', 'Doctor', 'Lt. Torries', 'Seven of Nine'],
    races=('Borg', 'Kason',),
    distance2earth=70000,
    coming_home=True)

nonedata = None

listofdictsdata = [dict(Erath=7390000000),
                   dict(Vulcan=6000000000),
                   dict(Kronos='unknown')]


def test_jsonbCol():
    connection = getConnection()
    if connection.dbName != "postgres":
        pytest.skip("These tests require PostgreSQL")

    setupClass([JsonbContainer], force=True)

    my_jsonb = JsonbContainer(
        jsondata=dictdata,
        jsondata_none=nonedata,
        jsondata_list=listofdictsdata)
    iid = my_jsonb.id

    JsonbContainer._connection.cache.clear()

    my_jsonb_2 = JsonbContainer.get(iid)

    assert my_jsonb_2.jsondata['coming_home'] == dictdata['coming_home']
    assert my_jsonb_2.jsondata['crew'] == dictdata['crew']
    assert my_jsonb_2.jsondata['races'] == ['Borg', 'Kason']
    assert my_jsonb_2.jsondata_none is None
    assert my_jsonb_2.jsondata_list == listofdictsdata
