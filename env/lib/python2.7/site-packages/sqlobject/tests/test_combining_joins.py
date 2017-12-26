from sqlobject import ForeignKey, ManyToMany, OneToMany, SQLObject, StringCol
from .dbtest import setupClass


class ComplexGroup(SQLObject):
    name = StringCol()
    complexes = OneToMany('Complex')

    def _get_unit_models(self):
        q = self.complexes.clause & Complex.unit_models.clause
        return UnitModel.select(q)


class Complex(SQLObject):
    name = StringCol()
    unit_models = ManyToMany('UnitModel')
    complex_group = ForeignKey('ComplexGroup')


class UnitModel(SQLObject):
    class sqlmeta:
        defaultOrderBy = 'name'
    name = StringCol()
    complexes = ManyToMany('Complex')


def test_join_sqlrepr():
    setupClass([ComplexGroup, UnitModel, Complex])
    cg1 = ComplexGroup(name='cg1')
    cg2 = ComplexGroup(name='cg2')
    c1 = Complex(name='c1', complex_group=cg1)
    c2 = Complex(name='c2', complex_group=cg2)
    c3 = Complex(name='c3', complex_group=cg2)
    u1 = UnitModel(name='u1')
    u2 = UnitModel(name='u2')
    u1.complexes.add(c1)
    u1.complexes.add(c2)
    u2.complexes.add(c2)
    u2.complexes.add(c3)
    assert list(Complex.selectBy(name='c1')) == [c1]

    assert list(cg1.unit_models) == [u1]
    assert list(cg2.unit_models) == [u1, u2, u2]
    assert list(cg2.unit_models.distinct()) == [u1, u2]

    assert list(
        cg2.unit_models.filter(UnitModel.q.name == 'u1')) == [u1]
