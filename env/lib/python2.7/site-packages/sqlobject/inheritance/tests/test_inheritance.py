from pytest import raises
from sqlobject import IntCol, StringCol
from sqlobject.inheritance import InheritableSQLObject
from sqlobject.tests.dbtest import setupClass

########################################
# Inheritance
########################################


class InheritablePerson(InheritableSQLObject):
    firstName = StringCol()
    lastName = StringCol(alternateID=True, length=255)


class Employee(InheritablePerson):
    _inheritable = False
    so_position = StringCol()


def setup():
    setupClass(InheritablePerson)
    setupClass(Employee)

    Employee(firstName='Project', lastName='Leader',
             so_position='Project leader')
    InheritablePerson(firstName='Oneof', lastName='Authors')


def test_creation_fail():
    setup()
    kwargs = {'firstName': 'John', 'lastname': 'Doe'}
    raises(TypeError, Employee, **kwargs)
    persons = InheritablePerson.select(InheritablePerson.q.firstName == 'John')
    assert persons.count() == 0


def test_inheritance():
    setup()

    persons = InheritablePerson.select()  # all
    for person in persons:
        assert isinstance(person, InheritablePerson)
        if isinstance(person, Employee):
            assert not hasattr(person, "childName")
        else:
            assert hasattr(person, "childName")
            assert not person.childName


def test_inheritance_select():
    setup()

    # comparison to None needed to build the right SQL expression
    persons = InheritablePerson.select(
        InheritablePerson.q.firstName != None)  # noqa
    assert persons.count() == 2

    persons = InheritablePerson.select(InheritablePerson.q.firstName == "phd")
    assert persons.count() == 0

    # comparison to None needed to build the right SQL expression
    employees = Employee.select(Employee.q.firstName != None)  # noqa
    assert employees.count() == 1

    employees = Employee.select(Employee.q.firstName == "phd")
    assert employees.count() == 0

    # comparison to None needed to build the right SQL expression
    employees = Employee.select(Employee.q.so_position != None)  # noqa
    assert employees.count() == 1

    persons = InheritablePerson.selectBy(firstName="Project")
    assert persons.count() == 1
    assert isinstance(persons[0], Employee)

    persons = Employee.selectBy(firstName="Project")
    assert persons.count() == 1

    try:
        person = InheritablePerson.byLastName("Oneof")
    except Exception:
        pass
    else:
        raise RuntimeError("unknown person %s" % person)

    person = InheritablePerson.byLastName("Leader")
    assert person.firstName == "Project"

    person = Employee.byLastName("Leader")
    assert person.firstName == "Project"

    persons = list(InheritablePerson.select(
        orderBy=InheritablePerson.q.lastName))
    assert len(persons) == 2

    persons = list(InheritablePerson.select(orderBy=(
        InheritablePerson.q.lastName, InheritablePerson.q.firstName)))
    assert len(persons) == 2

    persons = list(Employee.select(orderBy=Employee.q.lastName))
    assert len(persons) == 1

    persons = list(Employee.select(orderBy=(Employee.q.lastName,
                                            Employee.q.firstName)))
    assert len(persons) == 1

    persons = list(Employee.select(orderBy=Employee.q.so_position))
    assert len(persons) == 1

    persons = list(Employee.select(orderBy=(Employee.q.so_position,
                                            Employee.q.lastName)))
    assert len(persons) == 1


def test_addDelColumn():
    setup()

    assert hasattr(InheritablePerson, "firstName")
    assert hasattr(Employee, "firstName")
    assert hasattr(InheritablePerson.q, "firstName")
    assert hasattr(Employee.q, "firstName")

    Employee.sqlmeta.addColumn(IntCol('runtime', default=None))

    assert not hasattr(InheritablePerson, 'runtime')
    assert hasattr(Employee, 'runtime')
    assert not hasattr(InheritablePerson.q, 'runtime')
    assert hasattr(Employee.q, 'runtime')

    InheritablePerson.sqlmeta.addColumn(IntCol('runtime2', default=None))

    assert hasattr(InheritablePerson, 'runtime2')
    assert hasattr(Employee, 'runtime2')
    assert hasattr(InheritablePerson.q, 'runtime2')
    assert hasattr(Employee.q, 'runtime2')

    Employee.sqlmeta.delColumn('runtime')

    assert not hasattr(InheritablePerson, 'runtime')
    assert not hasattr(Employee, 'runtime')
    assert not hasattr(InheritablePerson.q, 'runtime')
    assert not hasattr(Employee.q, 'runtime')

    InheritablePerson.sqlmeta.delColumn('runtime2')

    assert not hasattr(InheritablePerson, 'runtime2')
    assert not hasattr(Employee, 'runtime2')
    assert not hasattr(InheritablePerson.q, 'runtime2')
    assert not hasattr(Employee.q, 'runtime2')
