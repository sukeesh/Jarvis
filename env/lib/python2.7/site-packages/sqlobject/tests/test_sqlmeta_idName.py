from sqlobject import MixedCaseStyle, SQLObject, sqlmeta
from sqlobject.tests.dbtest import setupClass


class myid_sqlmeta(sqlmeta):
    idName = "my_id"


class SOTestSqlmeta1(SQLObject):
    class sqlmeta(myid_sqlmeta):
        pass


class SOTestSqlmeta2(SQLObject):
    class sqlmeta(sqlmeta):
        style = MixedCaseStyle(longID=True)


class SOTestSqlmeta3(SQLObject):
    class sqlmeta(myid_sqlmeta):
        style = MixedCaseStyle(longID=True)


class SOTestSqlmeta4(SQLObject):
    class sqlmeta(myid_sqlmeta):
        idName = None
        style = MixedCaseStyle(longID=True)


class longid_sqlmeta(sqlmeta):
    idName = "my_id"
    style = MixedCaseStyle(longID=True)


class SOTestSqlmeta5(SQLObject):
    class sqlmeta(longid_sqlmeta):
        pass


class SOTestSqlmeta6(SQLObject):
    class sqlmeta(longid_sqlmeta):
        idName = None


def test_sqlmeta_inherited_idName():
    setupClass([SOTestSqlmeta1, SOTestSqlmeta2])
    assert SOTestSqlmeta1.sqlmeta.idName == "my_id"
    assert SOTestSqlmeta2.sqlmeta.idName == "SOTestSqlmeta2ID"
    assert SOTestSqlmeta3.sqlmeta.idName == "my_id"
    assert SOTestSqlmeta4.sqlmeta.idName == "SOTestSqlmeta4ID"
    assert SOTestSqlmeta5.sqlmeta.idName == "my_id"
    assert SOTestSqlmeta6.sqlmeta.idName == "SOTestSqlmeta6ID"
