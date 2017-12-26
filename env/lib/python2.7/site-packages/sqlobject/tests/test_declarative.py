from sqlobject.declarative import Declarative


class A1(Declarative):

    a = 1
    b = []


class A2(A1):

    a = 5

A3 = A2(b=5)


def test_a_classes():
    assert A1.a == 1
    assert A1.singleton().a == 1
    assert A1.b is A2.b
    assert A3.b == 5
    assert A1.declarative_count == A1.singleton().declarative_count
    assert A1.declarative_count < A2.declarative_count
    assert A2.singleton() is not A1.singleton()
    assert A3.singleton().b == A3.b


class B1(Declarative):

    attrs = []

    def __classinit__(cls, new_attrs):
        Declarative.__classinit__(cls, new_attrs)
        cls.attrs = cls.add_attrs(cls.attrs, new_attrs)

    def __instanceinit__(self, new_attrs):
        Declarative.__instanceinit__(self, new_attrs)
        self.attrs = self.add_attrs(self.attrs, new_attrs)

    @staticmethod
    def add_attrs(old_attrs, new_attrs):
        old_attrs = old_attrs[:]
        for name in new_attrs.keys():
            if (name in old_attrs or name.startswith('_') or
                    name in ('add_attrs', 'declarative_count', 'attrs')):
                continue
            old_attrs.append(name)
        old_attrs.sort()
        return old_attrs

    c = 1


class B2(B1):

    g = 3

    def __classinit__(cls, new_attrs):
        new_attrs['test'] = 'whatever'
        B1.__classinit__(cls, new_attrs)

B3 = B2(c=5, d=3)
B4 = B3(d=5)
B5 = B1(a=1)


def test_b_classes():
    assert B1.attrs == ['c']
    assert B1.c == 1
    assert B2.attrs == ['c', 'g', 'test']
    assert B3.d == 3
    assert B4.d == 5
    assert B5.a == 1
    assert B5.attrs == ['a', 'c']
    assert B3.attrs == ['c', 'd', 'g', 'test']
    assert B4.attrs == ['c', 'd', 'g', 'test']
    order = [B1, B1.singleton(), B2, B2.singleton(),
             B3, B3.singleton(), B4, B4.singleton(),
             B5, B5.singleton()]
    last = 0
    for obj in order:
        assert obj.declarative_count >= last
        last = obj.declarative_count
