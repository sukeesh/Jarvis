################################################################################
#  Copyright (C) 2002-2011  Travis Shirk <travis@pobox.com>
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
'''Top-level module.'''
import sys
import locale
from .compat import StringTypes


_DEFAULT_ENCODING = "latin1"

LOCAL_ENCODING = locale.getpreferredencoding(do_setlocale=True)
'''The local encoding, used when parsing command line options, console output,
etc. The default is always ``latin1`` if it cannot be determined, it is NOT
the value shown.'''
if not LOCAL_ENCODING or LOCAL_ENCODING == "ANSI_X3.4-1968":  # pragma: no cover
    LOCAL_ENCODING = _DEFAULT_ENCODING

LOCAL_FS_ENCODING = sys.getfilesystemencoding()
'''The local file system encoding, the default is ``latin1`` if it cannot be
determined.'''
if not LOCAL_FS_ENCODING:  # pragma: no cover
    LOCAL_FS_ENCODING = _DEFAULT_ENCODING


class Error(Exception):
    '''Base exception type for all eyed3 errors.'''
    def __init__(self, *args):
        super(Error, self).__init__(*args)
        if args:
            # The base class will do exactly this if len(args) == 1,
            # but not when > 1. Note, the 2.7 base class will, 3 will not.
            # Make it so.
            self.message = args[0]


def require(version_spec):
    '''Check for a specific version of eyeD3.
    Returns ``None`` when the loaded version of ``eyed3`` is <= ``version_spec``
    and raises a ``eyed3.Error`` otherwise. ``version_spec`` may be a string
    or int tuple. In either case at least **2** version values must be
    specified. For example, "0.7", (0,7,1), etc.

    API compatibility is currently based on major and minor version values,
    therefore neither version 0.6 or 0.8 is compatible for version 0.7.
    '''
    from .info import VERSION_TUPLE as CURRENT_VERSION

    def t2s(_t):
        return ".".join([str(v) for v in _t])

    req_version = None
    if type(version_spec) in StringTypes:
        req_version = tuple((int(v) for v in version_spec.split(".")))
    else:
        req_version = tuple(version_spec)

    if len(req_version) < 2:
        raise ValueError("At least 2 version values are required")
    elif len(req_version) < 3:
        # Pad with 0(s)
        req_version += (tuple([0]) * (3 - len(req_version)))

    # API compatibility is on major minor, so if the current version is greater
    # than either of these the 'require' will fail.
    for i in 0, 1:
        if CURRENT_VERSION[i] > req_version[i]:
            raise Error("eyeD3 v%s not compatible with v%s (required)" %
                        (t2s(CURRENT_VERSION), t2s(req_version)))

    # Is the required version greater than us
    if req_version > CURRENT_VERSION:
        raise Error("eyed3 v%s < v%s (required)" %
                    (t2s(CURRENT_VERSION), t2s(req_version)))


from .utils.log import log
from .core import load

del sys
del locale
