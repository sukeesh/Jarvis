from sqlobject import SQLObject, StringCol
from sqlobject.sqlbuilder import Alias, ImportProxy, tablesUsedSet
from sqlobject.views import ViewSQLObject


def testSimple():
    nyi = ImportProxy('NotYetImported')
    x = nyi.q.name

    class NotYetImported(SQLObject):
        name = StringCol(dbName='a_name')

    y = nyi.q.name

    assert str(x) == 'not_yet_imported.a_name'
    assert str(y) == 'not_yet_imported.a_name'


def testAddition():
    nyi = ImportProxy('NotYetImported2')
    x = nyi.q.name + nyi.q.name

    class NotYetImported2(SQLObject):
        name = StringCol(dbName='a_name')

    assert str(x) == \
        '((not_yet_imported2.a_name) + (not_yet_imported2.a_name))'


def testOnView():
    nyi = ImportProxy('NotYetImportedV')
    x = nyi.q.name

    class NotYetImported3(SQLObject):
        name = StringCol(dbName='a_name')

    class NotYetImportedV(ViewSQLObject):
        class sqlmeta:
            idName = NotYetImported3.q.id
        name = StringCol(dbName=NotYetImported3.q.name)

    assert str(x) == 'not_yet_imported_v.name'


def testAlias():
    nyi = ImportProxy('NotYetImported4')
    y = Alias(nyi, 'y')
    x = y.q.name

    class NotYetImported4(SQLObject):
        name = StringCol(dbName='a_name')

    assert str(y) == 'not_yet_imported4  y'
    assert tablesUsedSet(x, None) == set(['not_yet_imported4  y'])
    assert str(x) == 'y.a_name'
