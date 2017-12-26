from __future__ import print_function
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from sqlobject import IntCol, SQLObject, StringCol
from sqlobject.util.csvexport import export_csv, export_csv_zip
from .dbtest import setupClass


def assert_export(result, *args, **kw):
    f = StringIO()
    kw['writer'] = f
    export_csv(*args, **kw)
    s = f.getvalue().replace('\r\n', '\n')
    if result.strip() != s.strip():
        print('**Expected:')
        print(result)
        print('**Got:')
        print(s)
        assert result.strip() == s.strip()


class SimpleCSV(SQLObject):

    name = StringCol()
    address = StringCol()
    address.csvTitle = 'Street Address'
    hidden = StringCol()
    hidden.noCSV = True


class ComplexCSV(SQLObject):

    fname = StringCol()
    lname = StringCol()
    age = IntCol()
    extraCSVColumns = [('name', 'Full Name'), 'initials']
    # initials should end up at the end then:
    csvColumnOrder = ['name', 'fname', 'lname', 'age']

    def _get_name(self):
        return self.fname + ' ' + self.lname

    def _get_initials(self):
        return self.fname[0] + self.lname[0]


def test_simple():
    setupClass(SimpleCSV)
    SimpleCSV(name='Bob', address='432W', hidden='boo')
    SimpleCSV(name='Joe', address='123W', hidden='arg')
    assert_export("""\
name,Street Address
Bob,432W
Joe,123W
""", SimpleCSV, orderBy='name')
    assert_export("""\
name,Street Address
Joe,123W
Bob,432W
""", SimpleCSV, orderBy='address')
    assert_export("""\
name,Street Address
Joe,123W
""", SimpleCSV.selectBy(name='Joe'))


def test_complex():
    setupClass(ComplexCSV)
    ComplexCSV(fname='John', lname='Doe', age=40)
    ComplexCSV(fname='Bob', lname='Dylan', age=60)
    ComplexCSV(fname='Harriet', lname='Tubman', age=160)
    assert_export("""\
Full Name,fname,lname,age,initials
John Doe,John,Doe,40,JD
Bob Dylan,Bob,Dylan,60,BD
Harriet Tubman,Harriet,Tubman,160,HT
""", ComplexCSV, orderBy='lname')
    assert_export("""\
Full Name,fname,lname,age,initials
Bob Dylan,Bob,Dylan,60,BD
John Doe,John,Doe,40,JD
""", ComplexCSV.select(ComplexCSV.q.lname.startswith('D'), orderBy='fname'))


def test_zip():
    # Just exercise tests, doesn't actually test results
    setupClass(SimpleCSV)
    SimpleCSV(name='Bob', address='432W', hidden='boo')
    SimpleCSV(name='Joe', address='123W', hidden='arg')

    setupClass(ComplexCSV)
    ComplexCSV(fname='John', lname='Doe', age=40)
    ComplexCSV(fname='Bob', lname='Dylan', age=60)
    ComplexCSV(fname='Harriet', lname='Tubman', age=160)
    s = export_csv_zip([SimpleCSV, ComplexCSV])
    assert isinstance(s, bytes) and s
    s = export_csv_zip([SimpleCSV.selectBy(name='Bob'),
                        (ComplexCSV, list(ComplexCSV.selectBy(fname='John')))])
