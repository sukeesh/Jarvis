import pytest

from sqlobject import boundattributes
from sqlobject import declarative

pytestmark = pytest.mark.skipif('True')


class SOTestMe(object):
    pass


class AttrReplace(boundattributes.BoundAttribute):

    __unpackargs__ = ('replace',)

    replace = None

    @declarative.classinstancemethod
    def make_object(self, cls, added_class, attr_name, **attrs):
        if not self:
            return cls.singleton().make_object(
                added_class, attr_name, **attrs)
        self.replace.added_class = added_class
        self.replace.name = attr_name
        assert attrs['replace'] is self.replace
        del attrs['replace']
        self.replace.attrs = attrs
        return self.replace


class Holder:
    def __init__(self, name):
        self.holder_name = name

    def __repr__(self):
        return '<Holder %s>' % self.holder_name


def test_1():
    v1 = Holder('v1')
    v2 = Holder('v2')
    v3 = Holder('v3')

    class V2Class(AttrReplace):
        arg1 = 'nothing'
        arg2 = ['something']

    class A1(SOTestMe):
        a = AttrReplace(v1)
        v = V2Class(v2)

        class inline(AttrReplace):
            replace = v3
            arg3 = 'again'
            arg4 = 'so there'
    for n in ('a', 'v', 'inline'):
        assert getattr(A1, n).name == n
        assert getattr(A1, n).added_class is A1
    assert A1.a is v1
    assert A1.a.attrs == {}
    assert A1.v is v2
    assert A1.v.attrs == {'arg1': 'nothing', 'arg2': ['something']}
    assert A1.inline is v3
    assert A1.inline.attrs == {'arg3': 'again', 'arg4': 'so there'}
