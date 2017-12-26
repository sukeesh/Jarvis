from sqlobject import SQLObject, StringCol
from sqlobject.tests.dbtest import setupClass


########################################
# Lazy updates
########################################


class Lazy(SQLObject):

    class sqlmeta:
        lazyUpdate = True
    name = StringCol()
    other = StringCol(default='nothing')
    third = StringCol(default='third')


class TestLazyTest:

    def setup_method(self, meth):
        # All this stuff is so that we can track when the connection
        # does an actual update; we put in a new _SO_update method
        # that calls the original and sets an instance variable that
        # we can later check.
        setupClass(Lazy)
        self.conn = Lazy._connection
        self.conn.didUpdate = False
        self._oldUpdate = self.conn._SO_update
        newUpdate = (
            lambda so, values, s=self, c=self.conn, o=self._oldUpdate:
            self._alternateUpdate(so, values, c, o))
        self.conn._SO_update = newUpdate

    def teardown_method(self, meth):
        self.conn._SO_update = self._oldUpdate
        del self._oldUpdate

    def _alternateUpdate(self, so, values, conn, oldUpdate):
        conn.didUpdate = True
        return oldUpdate(so, values)

    def test_lazy(self):
        assert not self.conn.didUpdate
        obj = Lazy(name='tim')
        # We just did an insert, but not an update:
        assert not self.conn.didUpdate
        obj.set(name='joe')
        assert obj.sqlmeta.dirty
        assert obj.name == 'joe'
        assert not self.conn.didUpdate
        obj.syncUpdate()
        assert obj.name == 'joe'
        assert self.conn.didUpdate
        assert not obj.sqlmeta.dirty
        assert obj.name == 'joe'
        self.conn.didUpdate = False

        obj = Lazy(name='frank')
        obj.name = 'joe'
        assert not self.conn.didUpdate
        assert obj.sqlmeta.dirty
        assert obj.name == 'joe'
        obj.name = 'joe2'
        assert not self.conn.didUpdate
        assert obj.sqlmeta.dirty
        assert obj.name == 'joe2'
        obj.syncUpdate()
        assert obj.name == 'joe2'
        assert not obj.sqlmeta.dirty
        assert self.conn.didUpdate
        self.conn.didUpdate = False

        obj = Lazy(name='loaded')
        assert not obj.sqlmeta.dirty
        assert not self.conn.didUpdate
        assert obj.name == 'loaded'
        obj.name = 'unloaded'
        assert obj.sqlmeta.dirty
        assert obj.name == 'unloaded'
        assert not self.conn.didUpdate
        obj.sync()
        assert not obj.sqlmeta.dirty
        assert obj.name == 'unloaded'
        assert self.conn.didUpdate
        self.conn.didUpdate = False
        obj.name = 'whatever'
        assert obj.sqlmeta.dirty
        assert obj.name == 'whatever'
        assert not self.conn.didUpdate
        obj._SO_loadValue('name')
        assert obj.sqlmeta.dirty
        assert obj.name == 'whatever'
        assert not self.conn.didUpdate
        obj._SO_loadValue('other')
        assert obj.name == 'whatever'
        assert not self.conn.didUpdate
        obj.syncUpdate()
        assert self.conn.didUpdate
        self.conn.didUpdate = False

        # Now, check that get() doesn't screw
        # cached objects' validator state.
        obj_id = obj.id
        old_state = obj._SO_validatorState
        obj = Lazy.get(obj_id)
        assert not obj.sqlmeta.dirty
        assert not self.conn.didUpdate
        assert obj._SO_validatorState is old_state
        assert obj.name == 'whatever'
        obj.name = 'unloaded'
        assert obj.name == 'unloaded'
        assert obj.sqlmeta.dirty
        assert not self.conn.didUpdate
        # Fetch the object again with get() and
        # make sure sqlmeta.dirty is still set, as the
        # object should come from the cache.
        obj = Lazy.get(obj_id)
        assert obj.sqlmeta.dirty
        assert not self.conn.didUpdate
        assert obj.name == 'unloaded'
        obj.syncUpdate()
        assert self.conn.didUpdate
        assert not obj.sqlmeta.dirty
        self.conn.didUpdate = False

        # Then clear the cache, and try a get()
        # again, to make sure stuf like _SO_createdValues
        # is properly initialized.
        self.conn.cache.clear()
        obj = Lazy.get(obj_id)
        assert not obj.sqlmeta.dirty
        assert not self.conn.didUpdate
        assert obj.name == 'unloaded'
        obj.name = 'spongebob'
        assert obj.name == 'spongebob'
        assert obj.sqlmeta.dirty
        assert not self.conn.didUpdate
        obj.syncUpdate()
        assert self.conn.didUpdate
        assert not obj.sqlmeta.dirty
        self.conn.didUpdate = False

        obj = Lazy(name='last')
        assert not obj.sqlmeta.dirty
        obj.syncUpdate()
        assert not self.conn.didUpdate
        assert not obj.sqlmeta.dirty
        # Check that setting multiple values
        # actually works. This was broken
        # and just worked because we were testing
        # only one value at a time, so 'name'
        # had the right value after the for loop *wink*
        # Also, check that passing a name that is not
        # a valid column doesn't break, but instead
        # just does a plain setattr.
        obj.set(name='first', other='who', third='yes')
        assert obj.name == 'first'
        assert obj.other == 'who'
        assert obj.third == 'yes'
        assert obj.sqlmeta.dirty
        assert not self.conn.didUpdate
        obj.syncUpdate()
        assert self.conn.didUpdate
        assert not obj.sqlmeta.dirty
