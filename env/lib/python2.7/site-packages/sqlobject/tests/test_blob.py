import pytest
from sqlobject import BLOBCol, SQLObject
from sqlobject.compat import PY2
from sqlobject.tests.dbtest import setupClass, supports


########################################
# BLOB columns
########################################


class ImageData(SQLObject):
    image = BLOBCol(default=b'emptydata', length=256)


def test_BLOBCol():
    if not supports('blobData'):
        pytest.skip("blobData isn't supported")
    setupClass(ImageData)
    if PY2:
        data = ''.join([chr(x) for x in range(256)])
    else:
        data = bytes(range(256))

    prof = ImageData()
    prof.image = data
    iid = prof.id

    ImageData._connection.cache.clear()

    prof2 = ImageData.get(iid)
    assert prof2.image == data
