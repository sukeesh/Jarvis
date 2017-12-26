from __future__ import print_function

from sqlobject import ForeignKey, ManyToMany, OneToMany, SQLObject, StringCol
from sqlobject.tests.dbtest import setupClass


########################################
# Joins
########################################


class PersonJNew(SQLObject):

    name = StringCol(length=40, alternateID=True)
    addressJs = ManyToMany('AddressJNew')


class AddressJNew(SQLObject):

    zip = StringCol(length=5, alternateID=True)
    personJs = ManyToMany('PersonJNew')


class ImplicitJoiningSONew(SQLObject):
    foo = ManyToMany('Bar')


class ExplicitJoiningSONew(SQLObject):
    foo = OneToMany('Bar')


class TestJoin:

    def setup_method(self, meth):
        setupClass(PersonJNew)
        setupClass(AddressJNew)
        for n in ['bob', 'tim', 'jane', 'joe', 'fred', 'barb']:
            PersonJNew(name=n)
        for z in ['11111', '22222', '33333', '44444']:
            AddressJNew(zip=z)

    def test_join(self):
        b = PersonJNew.byName('bob')
        assert list(b.addressJs) == []
        z = AddressJNew.byZip('11111')
        b.addressJs.add(z)
        self.assertZipsEqual(b.addressJs, ['11111'])
        print(str(z.personJs), repr(z.personJs))
        self.assertNamesEqual(z.personJs, ['bob'])
        z2 = AddressJNew.byZip('22222')
        b.addressJs.add(z2)
        print(str(b.addressJs))
        self.assertZipsEqual(b.addressJs, ['11111', '22222'])
        self.assertNamesEqual(z2.personJs, ['bob'])
        b.addressJs.remove(z)
        self.assertZipsEqual(b.addressJs, ['22222'])
        self.assertNamesEqual(z.personJs, [])

    def assertZipsEqual(self, zips, dest):
        assert [a.zip for a in zips] == dest

    def assertNamesEqual(self, people, dest):
        assert [p.name for p in people] == dest

    def test_joinAttributeWithUnderscores(self):
        # Make sure that the implicit setting of joinMethodName works
        assert hasattr(ImplicitJoiningSONew, 'foo')
        assert not hasattr(ImplicitJoiningSONew, 'bars')

        # And make sure explicit setting also works
        assert hasattr(ExplicitJoiningSONew, 'foo')
        assert not hasattr(ExplicitJoiningSONew, 'bars')


class PersonJNew2(SQLObject):

    name = StringCol('name', length=40, alternateID=True)
    addressJ2s = OneToMany('AddressJNew2')


class AddressJNew2(SQLObject):

    class sqlmeta:
        defaultOrder = ['-zip', 'plus4']

    zip = StringCol(length=5)
    plus4 = StringCol(length=4, default=None)
    personJNew2 = ForeignKey('PersonJNew2')


class TestJoin2:

    def setup_method(self, meth):
        setupClass([PersonJNew2, AddressJNew2])
        p1 = PersonJNew2(name='bob')
        p2 = PersonJNew2(name='sally')
        for z in ['11111', '22222', '33333']:
            AddressJNew2(zip=z, personJNew2=p1)
        AddressJNew2(zip='00000', personJNew2=p2)

    def test_basic(self):
        bob = PersonJNew2.byName('bob')
        sally = PersonJNew2.byName('sally')
        print(bob.addressJ2s)
        print(bob)
        assert len(list(bob.addressJ2s)) == 3
        assert len(list(sally.addressJ2s)) == 1
        bob.addressJ2s[0].destroySelf()
        assert len(list(bob.addressJ2s)) == 2
        z = bob.addressJ2s[0]
        z.zip = 'xxxxx'
        id = z.id
        del z
        z = AddressJNew2.get(id)
        assert z.zip == 'xxxxx'

    def test_defaultOrder(self):
        p1 = PersonJNew2.byName('bob')
        assert ([i.zip for i in p1.addressJ2s] ==
                ['33333', '22222', '11111'])


_personJ3_getters = []
_personJ3_setters = []


class PersonJNew3(SQLObject):

    name = StringCol('name', length=40, alternateID=True)
    addressJNew3s = OneToMany('AddressJNew3')


class AddressJNew3(SQLObject):

    zip = StringCol(length=5)
    personJNew3 = ForeignKey('PersonJNew3')

    def _get_personJNew3(self):
        value = self._SO_get_personJNew3()
        _personJ3_getters.append((self, value))
        return value

    def _set_personJNew3(self, value):
        self._SO_set_personJNew3(value)
        _personJ3_setters.append((self, value))


class TestJoin3:

    def setup_method(self, meth):
        setupClass([PersonJNew3, AddressJNew3])
        p1 = PersonJNew3(name='bob')
        p2 = PersonJNew3(name='sally')
        for z in ['11111', '22222', '33333']:
            AddressJNew3(zip=z, personJNew3=p1)
        AddressJNew3(zip='00000', personJNew3=p2)

    def test_accessors(self):
        assert len(list(_personJ3_getters)) == 0
        assert len(list(_personJ3_setters)) == 4
        bob = PersonJNew3.byName('bob')
        for addressJ3 in bob.addressJNew3s:
            addressJ3.personJNew3
        assert len(list(_personJ3_getters)) == 3
        assert len(list(_personJ3_setters)) == 4
