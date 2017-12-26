# These tests are not enabled yet, but here are some working examples
# of using createSQL so far.

from sqlobject import SQLObject, StringCol


class SOTest1(SQLObject):
    class sqlmeta:
        createSQL = "CREATE SEQUENCE db_test1_seq;"
    test1 = StringCol()


class SOTest2(SQLObject):
    class sqlmeta:
        createSQL = ["CREATE SEQUENCE db_test2_seq;",
                     "ALTER TABLE test2 ADD CHECK(test2 != '');"]
    test2 = StringCol()


class SOTest3(SQLObject):
    class sqlmeta:
        createSQL = {'postgres': 'CREATE SEQUENCE db_test3_seq;',
                     'mysql': 'CREATE SEQUENCE db_test3_seq;'}
    test3 = StringCol()


class SOTest4(SQLObject):
    class sqlmeta:
        createSQL = {'postgres': ['CREATE SEQUENCE db_test4_seq;',
                                  "ALTER TABLE test4 ADD CHECK(test4 != '');"],
                     'mysql': 'CREATE SEQUENCE db_test4_seq;'}
    test4 = StringCol()


class SOTest5(SQLObject):
    class sqlmeta:
        createSQL = {'mysql': 'CREATE SEQUENCE db_test5_seq;'}
    test5 = StringCol()
