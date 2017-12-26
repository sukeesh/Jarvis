from sqlobject import ForeignKey, SQLObject, StringCol
from sqlobject.tests.dbtest import setupClass
from sqlobject.inheritance import InheritableSQLObject


class Note(SQLObject):
    text = StringCol()


class PersonWithNotes(InheritableSQLObject):
    firstName = StringCol()
    lastName = StringCol()
    note = ForeignKey("Note", default=None)


class Paper(SQLObject):
    content = StringCol()


class EmployeeWithNotes(PersonWithNotes):
    _inheritable = False
    paper = ForeignKey("Paper", default=None)


def test_foreignKey():
    setupClass([Note, PersonWithNotes, Paper, EmployeeWithNotes], force=True)

    note = Note(text="person")
    PersonWithNotes(firstName='Oneof', lastName='Authors', note=note)
    note = Note(text="employee")
    EmployeeWithNotes(firstName='Project', lastName='Leader', note=note)

    paper = Paper(content="secret")
    EmployeeWithNotes(firstName='Senior', lastName='Clerk', paper=paper)
    PersonWithNotes(firstName='Some', lastName='Person')

    person = PersonWithNotes.get(1)
    assert isinstance(person, PersonWithNotes) and \
        not isinstance(person, EmployeeWithNotes)
    assert person.note.text == "person"

    employee = EmployeeWithNotes.get(2)
    assert isinstance(employee, EmployeeWithNotes)
    assert employee.note.text == "employee"
    save_employee = employee

    # comparison to None needed to build the right SQL expression
    persons = PersonWithNotes.select(PersonWithNotes.q.noteID != None)  # noqa
    assert persons.count() == 2

    persons = PersonWithNotes.selectBy(noteID=person.note.id)
    assert persons.count() == 1

    # comparison to None needed to build the right SQL expression
    employee = EmployeeWithNotes.select(
        PersonWithNotes.q.noteID != None)  # noqa
    assert employee.count() == 1

    persons = PersonWithNotes.selectBy(noteID=person.note.id)
    assert persons.count() == 1

    persons = PersonWithNotes.selectBy(note=person.note)
    assert persons.count() == 1

    persons = PersonWithNotes.selectBy(note=None)
    assert persons.count() == 2

    employee = EmployeeWithNotes.selectBy(paperID=None)
    assert employee.count() == 1

    employee = EmployeeWithNotes.selectBy(paper=None)
    assert employee.count() == 1

    employee = EmployeeWithNotes.selectBy(note=save_employee.note,
                                          paper=save_employee.paper)
    assert employee.count() == 1

    employee = EmployeeWithNotes.selectBy()
    assert employee.count() == 2


class SOTestInhBase(InheritableSQLObject):
    pass


class SOTestInhFKey(SOTestInhBase):
    base = ForeignKey("SOTestInhBase")


def test_foreignKey2():
    setupClass([SOTestInhBase, SOTestInhFKey])

    test = SOTestInhBase()
    SOTestInhFKey(base=test)
