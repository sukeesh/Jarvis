from sqlobject import DatabaseIndex, IntCol, StringCol
from sqlobject.tests.dbtest import setupClass
from sqlobject.inheritance import InheritableSQLObject


class InhPersonIdxGet(InheritableSQLObject):
    first_name = StringCol(notNone=True, length=100)
    last_name = StringCol(notNone=True, length=100)
    age = IntCol()
    pk = DatabaseIndex(first_name, last_name, unique=True)


class InhEmployeeIdxGet(InhPersonIdxGet):
    security_number = IntCol()
    experience = IntCol()
    sec_index = DatabaseIndex(security_number, unique=True)


class InhSalesManIdxGet(InhEmployeeIdxGet):
    _inheritable = False
    skill = IntCol()


def test_index_get_1():
    setupClass([InhPersonIdxGet, InhEmployeeIdxGet, InhSalesManIdxGet])

    InhSalesManIdxGet(first_name='Michael', last_name='Pallin', age=65,
                      security_number=2304, experience=2, skill=10)
    InhEmployeeIdxGet(first_name='Eric', last_name='Idle', age=63,
                      security_number=3402, experience=9)
    InhPersonIdxGet(first_name='Terry', last_name='Guilliam', age=64)

    InhPersonIdxGet.pk.get('Michael', 'Pallin')
    InhEmployeeIdxGet.pk.get('Michael', 'Pallin')
    InhSalesManIdxGet.pk.get('Michael', 'Pallin')
    InhPersonIdxGet.pk.get('Eric', 'Idle')
    InhEmployeeIdxGet.pk.get('Eric', 'Idle')
    InhPersonIdxGet.pk.get(first_name='Terry', last_name='Guilliam')
    InhEmployeeIdxGet.sec_index.get(2304)
    InhEmployeeIdxGet.sec_index.get(3402)
    InhSalesManIdxGet.sec_index.get(2304)
    InhSalesManIdxGet.sec_index.get(3402)
