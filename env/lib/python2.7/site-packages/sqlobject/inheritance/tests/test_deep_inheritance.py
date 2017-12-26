from pytest import raises, skip
from sqlobject import ForeignKey, MultipleJoin, StringCol
from sqlobject.inheritance import InheritableSQLObject
from sqlobject.tests.dbtest import getConnection, setupClass, supports

########################################
# Deep Inheritance
########################################


class DIPerson(InheritableSQLObject):
    firstName = StringCol(length=100)
    lastName = StringCol(alternateID=True, length=255)
    manager = ForeignKey("DIManager", default=None)


class DIEmployee(DIPerson):
    so_position = StringCol(unique=True, length=100)


class DIManager(DIEmployee):
    subdudes = MultipleJoin("DIPerson", joinColumn="manager_id")


def test_creation_fail():
    """
    Try to create a Manager without specifying a position.
    This should fail without leaving any partial records in
    the database.

    """
    setupClass([DIManager, DIEmployee, DIPerson])

    kwargs = {'firstName': 'John', 'lastname': 'Doe'}
    raises(TypeError, DIManager, **kwargs)
    persons = DIEmployee.select(DIPerson.q.firstName == 'John')
    assert persons.count() == 0


def test_creation_fail2():
    """
    Try to create two Managers with the same position.
    This should fail without leaving any partial records in
    the database.

    """
    setupClass([DIManager, DIEmployee, DIPerson])

    kwargs = {'firstName': 'John', 'lastName': 'Doe',
              'so_position': 'Project Manager'}
    DIManager(**kwargs)
    persons = DIEmployee.select(DIPerson.q.firstName == 'John')
    assert persons.count() == 1

    kwargs = {'firstName': 'John', 'lastName': 'Doe II',
              'so_position': 'Project Manager'}
    raises(Exception, DIManager, **kwargs)
    persons = DIPerson.select(DIPerson.q.firstName == 'John')
    assert persons.count() == 1

    if not supports('transactions'):
        skip("Transactions aren't supported")
    transaction = DIPerson._connection.transaction()
    kwargs = {'firstName': 'John', 'lastName': 'Doe III',
              'so_position': 'Project Manager'}
    raises(Exception, DIManager, connection=transaction, **kwargs)
    transaction.rollback()
    transaction.begin()
    persons = DIPerson.select(DIPerson.q.firstName == 'John',
                              connection=transaction)
    assert persons.count() == 1


def test_deep_inheritance():
    setupClass([DIManager, DIEmployee, DIPerson])

    manager = DIManager(firstName='Project', lastName='Manager',
                        so_position='Project Manager')
    manager_id = manager.id
    employee_id = DIEmployee(firstName='Project', lastName='Leader',
                             so_position='Project leader', manager=manager).id
    DIPerson(firstName='Oneof', lastName='Authors', manager=manager)

    conn = getConnection()
    cache = conn.cache
    cache.clear()

    managers = list(DIManager.select())
    assert len(managers) == 1
    cache.clear()

    employees = list(DIEmployee.select())
    assert len(employees) == 2
    cache.clear()

    persons = list(DIPerson.select())
    assert len(persons) == 3
    cache.clear()

    person = DIPerson.get(employee_id)
    assert isinstance(person, DIEmployee)

    person = DIPerson.get(manager_id)
    assert isinstance(person, DIEmployee)
    assert isinstance(person, DIManager)
    cache.clear()

    person = DIEmployee.get(manager_id)
    assert isinstance(person, DIManager)
    conn.close()
