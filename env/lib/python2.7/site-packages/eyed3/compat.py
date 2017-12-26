# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2013  Travis Shirk <travis@pobox.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.
#
################################################################################
'''
Compatibility for various versions of Python (e.g. 2.6, 2.7, and 3.3)
'''
import os
import sys
import types


PY2 = sys.version_info[0] == 2
PY26 = sys.version_info[0:2] == (2, 6)

if PY2:
    StringTypes = types.StringTypes
    UnicodeType = unicode
    BytesType = str
    unicode = unicode

    from ConfigParser import SafeConfigParser as ConfigParser
    from ConfigParser import Error as ConfigParserError

    from StringIO import StringIO
else:
    StringTypes = (str,)
    UnicodeType = str
    BytesType = bytes
    unicode = str

    from configparser import ConfigParser
    from configparser import Error as ConfigParserError

    from io import StringIO


def toByteString(n):
    if PY2:
        return chr(n)
    else:
        return bytes((n,))


def byteiter(bites):
    assert(isinstance(bites, str if PY2 else bytes))
    for b in bites:
        yield b if PY2 else bytes((b,))

if not PY26:
    from functools import total_ordering
else:
    def total_ordering(cls):  # noqa
        """Class decorator that fills in missing ordering methods"""
        convert = {
            '__lt__': [('__gt__', lambda self, other: other < self),
                    ('__le__', lambda self, other: not other < self),
                    ('__ge__', lambda self, other: not self < other)],
            '__le__': [('__ge__', lambda self, other: other <= self),
                    ('__lt__', lambda self, other: not other <= self),
                    ('__gt__', lambda self, other: not self <= other)],
            '__gt__': [('__lt__', lambda self, other: other > self),
                    ('__ge__', lambda self, other: not other > self),
                    ('__le__', lambda self, other: not self > other)],
            '__ge__': [('__le__', lambda self, other: other >= self),
                    ('__gt__', lambda self, other: not other >= self),
                    ('__lt__', lambda self, other: not self >= other)]
        }
        roots = set(dir(cls)) & set(convert)
        if not roots:
            raise ValueError('must define at least one ordering operation: '
                             '< > <= >=')  # noqa
        root = max(roots)       # prefer __lt__ to __le__ to __gt__ to __ge__
        for opname, opfunc in convert[root]:
            if opname not in roots:
                opfunc.__name__ = opname
                opfunc.__doc__ = getattr(int, opname).__doc__
                setattr(cls, opname, opfunc)
        return cls


def importmod(mod_file):
    '''Imports a Ptyhon module referenced by absolute or relative path
    ``mod_file``. The module is retured.'''
    mod_name = os.path.splitext(os.path.basename(mod_file))[0]

    if PY2:
        import imp
        mod = imp.load_source(mod_name, mod_file)
    else:
        import importlib.machinery
        loader = importlib.machinery.SourceFileLoader(mod_name, mod_file)
        mod = loader.load_module()

    return mod

