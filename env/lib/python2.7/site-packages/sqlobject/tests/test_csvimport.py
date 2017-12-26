import csv
from datetime import datetime
from sqlobject.util.csvimport import load_csv

csv_data = """\
name:str,age:datetime,value:int
Test,2000-01-01 21:44:33,42"""


def test_load_csv():
    loaded = load_csv(csv.reader(csv_data.split('\n')),
                      default_class='SQLObject')
    assert loaded == {
        'SQLObject': [
            {
                'age': datetime(2000, 1, 1, 21, 44, 33),
                'name': 'Test',
                'value': 42
            }
        ]
    }
