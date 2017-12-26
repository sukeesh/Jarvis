from sqlobject.compat import PY2
from sqlobject.constraints import BadValue, InList, MaxLength, \
    isFloat, isInt, isString, notNull
from sqlobject.tests.dbtest import Dummy, raises

if not PY2:
    # alias for python 3 compatability
    long = int


def test_constraints():
    obj = 'Test object'
    col = Dummy(name='col')
    isString(obj, col, 'blah')
    raises(BadValue, isString, obj, col, 1)
    if PY2:
        # @@: Should this really be an error?
        raises(BadValue, isString, obj, col, u'test!')
    else:
        raises(BadValue, isString, obj, col, b'test!')
    # isString(obj, col, u'test!')

    raises(BadValue, notNull, obj, col, None)
    raises(BadValue, isInt, obj, col, 1.1)
    isInt(obj, col, 1)
    isInt(obj, col, long(1))
    isFloat(obj, col, 1)
    isFloat(obj, col, long(1))
    isFloat(obj, col, 1.2)
    raises(BadValue, isFloat, obj, col, '1.0')

    # @@: Should test isBool, but I don't think isBool is right

    lst = InList(('a', 'b', 'c'))
    lst(obj, col, 'a')
    raises(BadValue, lst, obj, col, ('a', 'b', 'c'))
    raises(BadValue, lst, obj, col, 'A')

    maxlen = MaxLength(2)
    raises(BadValue, maxlen, obj, col, '123')
    maxlen(obj, col, '12')
    maxlen(obj, col, (1,))
    raises(BadValue, maxlen, obj, col, 1)
