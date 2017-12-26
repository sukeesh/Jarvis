from hashlib import sha256, md5
from sqlobject import AND, IntCol, OR, SQLObject
from sqlobject.compat import PY2
from sqlobject.include import hashcol
from sqlobject.tests.dbtest import setupClass

########################################
# HashCol test
########################################

if PY2:
    def sha256_str(x):
        return sha256(x).hexdigest()

    def md5_str(x):
        return md5(x).hexdigest()
else:
    def sha256_str(x):
        return sha256(x.encode('utf8')).hexdigest()

    def md5_str(x):
        return md5(x.encode('utf8')).hexdigest()


class HashTest(SQLObject):
    so_count = IntCol(alternateID=True)
    col1 = hashcol.HashCol()
    col2 = hashcol.HashCol(hashMethod=sha256_str)


data = ['test', 'This is more text', 'test 2']
items = []


def setup():
    global items
    items = []
    setupClass(HashTest)
    for i, s in enumerate(data):
        items.append(HashTest(so_count=i, col1=s, col2=s))


def test_create():
    setup()
    for s, item in zip(data, items):
        assert item.col1 == s
        assert item.col2 == s

    conn = HashTest._connection
    rows = conn.queryAll("""
    SELECT so_count, col1, col2
    FROM hash_test
    ORDER BY so_count
    """)
    for so_count, col1, col2 in rows:
        assert md5_str(data[so_count]) == col1
        assert sha256_str(data[so_count]) == col2


def test_select():
    for i, value in enumerate(data):
        rows = list(HashTest.select(HashTest.q.col1 == value))
        assert len(rows) == 1
        rows = list(HashTest.select(HashTest.q.col2 == value))
        assert len(rows) == 1
        # Passing the hash in directly should fail
        rows = list(HashTest.select(HashTest.q.col2 == sha256_str(value)))
        assert len(rows) == 0
        rows = list(HashTest.select(AND(
            HashTest.q.col1 == value,
            HashTest.q.col2 == value
        )))
        assert len(rows) == 1
        rows = list(HashTest.selectBy(col1=value))
        assert len(rows) == 1
        rows = list(HashTest.selectBy(col2=value))
        assert len(rows) == 1
        rows = list(HashTest.selectBy(col1=value, col2=value))
        assert len(rows) == 1
    rows = list(HashTest.select(OR(
        HashTest.q.col1 == 'test 2',
        HashTest.q.col2 == 'test'
    )))
    assert len(rows) == 2
