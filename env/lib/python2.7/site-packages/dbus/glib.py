# Copyright (C) 2004 Anders Carlsson
# Copyright (C) 2004, 2005, 2006 Red Hat Inc. <http://www.redhat.com/>
# Copyright (C) 2005, 2006 Collabora Ltd. <http://www.collabora.co.uk/>
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

"""Deprecated module which sets the default GLib main context as the mainloop
implementation within D-Bus, as a side-effect of being imported!

This API is highly non-obvious, so instead of importing this module,
new programs which don't need pre-0.80 compatibility should use this
equivalent code::

    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)
"""
__docformat__ = 'restructuredtext'

from dbus.mainloop.glib import DBusGMainLoop, threads_init
from warnings import warn as _warn

init_threads = threads_init

DBusGMainLoop(set_as_default=True)

_warn(DeprecationWarning("""\
Importing dbus.glib to use the GLib main loop with dbus-python is deprecated.
Instead, use this sequence:

    from dbus.mainloop.glib import DBusGMainLoop

    DBusGMainLoop(set_as_default=True)
"""), DeprecationWarning, stacklevel=2)
