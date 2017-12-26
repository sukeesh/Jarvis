from sqlobject import ForeignKey, SQLObject, StringCol, sqlmeta, styles
from sqlobject.tests.dbtest import setupClass


class AnotherStyle(styles.MixedCaseUnderscoreStyle):
    def pythonAttrToDBColumn(self, attr):
        if attr.lower().endswith('id'):
            return 'id' + styles.MixedCaseUnderscoreStyle.\
                pythonAttrToDBColumn(self, attr[:-2])
        else:
            return styles.MixedCaseUnderscoreStyle.\
                pythonAttrToDBColumn(self, attr)


class SOStyleTest1(SQLObject):
    a = StringCol()
    st2 = ForeignKey('SOStyleTest2')

    class sqlmeta(sqlmeta):
        style = AnotherStyle()


class SOStyleTest2(SQLObject):
    b = StringCol()

    class sqlmeta(sqlmeta):
        style = AnotherStyle()


def test_style():
    setupClass([SOStyleTest2, SOStyleTest1])
    st1 = SOStyleTest1(a='something', st2=None)
    st2 = SOStyleTest2(b='whatever')
    st1.st2 = st2
    assert st1.sqlmeta.columns['st2ID'].dbName == 'idst2'
    assert st1.st2 == st2
