import sqlobject.col
from sqlobject.compat import PY2, string_type


__all__ = ['HashCol']


class DbHash:
    """ Presents a comparison object for hashes, allowing plain text to be
    automagically compared with the base content. """

    def __init__(self, hash, hashMethod):
        self.hash = hash
        self.hashMethod = hashMethod

    def _get_key(self, other):
        """Create the hash of the other class"""
        if not isinstance(other, string_type):
            raise TypeError(
                "A hash may only be compared with a string, or None.")
        return self.hashMethod(other)

    def __eq__(self, other):
        if other is None:
            if self.hash is None:
                return True
            return False
        other_key = self._get_key(other)
        return other_key == self.hash

    def __lt__(self, other):
        if other is None:
            return False
        other_key = self._get_key(other)
        return other_key < self.hash

    def __gt__(self, other):
        if other is None:
            if self.hash is None:
                return False
            return True
        other_key = self._get_key(other)
        return other_key > self.hash

    def __le__(self, other):
        if other is None:
            if self.hash is None:
                return True
            return False
        other_key = self._get_key(other)
        return other_key <= self.hash

    def __ge__(self, other):
        if other is None:
            return True
        other_key = self._get_key(other)
        return other_key >= self.hash

    def __repr__(self):
        return "<DbHash>"


class HashValidator(sqlobject.col.StringValidator):
    """ Provides formal SQLObject validation services for the HashCol. """

    def to_python(self, value, state):
        """ Passes out a hash object. """
        if value is None:
            return None
        return DbHash(hash=value, hashMethod=self.hashMethod)

    def from_python(self, value, state):
        """ Store the given value as a MD5 hash, or None if specified. """
        if value is None:
            return None
        return self.hashMethod(value)


class SOHashCol(sqlobject.col.SOStringCol):
    """ The internal HashCol definition. By default, enforces a md5 digest. """

    def __init__(self, **kw):
        if 'hashMethod' not in kw:
            from hashlib import md5
            if PY2:
                self.hashMethod = lambda v: md5(v).hexdigest()
            else:
                self.hashMethod = lambda v: md5(v.encode('utf8')).hexdigest()
            if 'length' not in kw:
                kw['length'] = 32
        else:
            self.hashMethod = kw['hashMethod']
            del kw['hashMethod']
        super(SOHashCol, self).__init__(**kw)

    def createValidators(self):
        return [HashValidator(name=self.name, hashMethod=self.hashMethod)] + \
            super(SOHashCol, self).createValidators()


class HashCol(sqlobject.col.StringCol):
    """ End-user HashCol class. May be instantiated with 'hashMethod', a function
    which returns the string hash of any other string (i.e. basestring). """

    baseClass = SOHashCol
