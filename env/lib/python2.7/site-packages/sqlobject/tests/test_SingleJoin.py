from sqlobject import ForeignKey, SQLObject, SingleJoin, StringCol
from sqlobject.tests.dbtest import setupClass


class PersonWithAlbum(SQLObject):
    name = StringCol()
    # albumNone returns the album or none
    albumNone = SingleJoin('PhotoAlbum', joinColumn='test_person_id')
    # albumInstance returns the album or an default album instance
    albumInstance = SingleJoin('PhotoAlbum', makeDefault=True,
                               joinColumn='test_person_id')


class PhotoAlbum(SQLObject):
    color = StringCol(default='red')
    person = ForeignKey('PersonWithAlbum', dbName='test_person_id')


def test_1():
    setupClass([PersonWithAlbum, PhotoAlbum])

    person = PersonWithAlbum(name='Gokou (Kakarouto)')
    # We didn't create an album, this way it returns None
    assert not person.albumNone
    assert isinstance(person.albumInstance, PhotoAlbum)

    PhotoAlbum(person=person)
    assert person.albumNone
    assert isinstance(person.albumNone, PhotoAlbum)
    assert isinstance(person.albumInstance, PhotoAlbum)
