# Copyright (C) 2006 Collabora Ltd. <http://www.collabora.co.uk/>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""Base definitions, etc. for main loop integration.

"""

import _dbus_bindings

NativeMainLoop = _dbus_bindings.NativeMainLoop

NULL_MAIN_LOOP = _dbus_bindings.NULL_MAIN_LOOP
"""A null mainloop which doesn't actually do anything.

For advanced users who want to dispatch events by hand. This is almost
certainly a bad idea - if in doubt, use the GLib main loop found in
`dbus.mainloop.glib`.
"""

WATCH_READABLE = _dbus_bindings.WATCH_READABLE
"""Represents a file descriptor becoming readable.
Used to implement file descriptor watches."""

WATCH_WRITABLE = _dbus_bindings.WATCH_WRITABLE
"""Represents a file descriptor becoming readable.
Used to implement file descriptor watches."""

WATCH_HANGUP = _dbus_bindings.WATCH_HANGUP
"""Represents a file descriptor reaching end-of-file.
Used to implement file descriptor watches."""

WATCH_ERROR = _dbus_bindings.WATCH_ERROR
"""Represents an error condition on a file descriptor.
Used to implement file descriptor watches."""

__all__ = (
           # Imported into this module
           'NativeMainLoop', 'WATCH_READABLE', 'WATCH_WRITABLE',
           'WATCH_HANGUP', 'WATCH_ERROR', 'NULL_MAIN_LOOP',

           # Submodules
           'glib'
           )
