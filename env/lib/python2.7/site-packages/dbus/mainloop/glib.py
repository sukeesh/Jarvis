# Copyright (C) 2004 Anders Carlsson
# Copyright (C) 2004-2006 Red Hat Inc. <http://www.redhat.com/>
# Copyright (C) 2005-2006 Collabora Ltd. <http://www.collabora.co.uk/>
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

"""GLib main loop integration using libdbus-glib."""

__all__ = ('DBusGMainLoop', 'threads_init')

from _dbus_glib_bindings import DBusGMainLoop, gthreads_init

_dbus_gthreads_initialized = False
def threads_init():
    """Initialize threads in dbus-glib, if this has not already been done.

    This must be called before creating a second thread in a program that
    uses this module.
    """
    global _dbus_gthreads_initialized
    if not _dbus_gthreads_initialized:
        gthreads_init()
        _dbus_gthreads_initialized = True
