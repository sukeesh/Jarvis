"""\
Implements the public API for a D-Bus client. See the dbus.service module
to export objects or claim well-known names.

..
  for epydoc's benefit

:NewField SupportedUsage: Supported usage
:NewField Constructor: Constructor
"""

# Copyright (C) 2003, 2004, 2005, 2006 Red Hat Inc. <http://www.redhat.com/>
# Copyright (C) 2003 David Zeuthen
# Copyright (C) 2004 Rob Taylor
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

__all__ = [
           # from _dbus
           'Bus', 'SystemBus', 'SessionBus', 'StarterBus',

           # from proxies
           'Interface',

           # from _dbus_bindings
           'get_default_main_loop', 'set_default_main_loop',

           'validate_interface_name', 'validate_member_name',
           'validate_bus_name', 'validate_object_path',
           'validate_error_name',

           'BUS_DAEMON_NAME', 'BUS_DAEMON_PATH', 'BUS_DAEMON_IFACE',
           'LOCAL_PATH', 'LOCAL_IFACE', 'PEER_IFACE',
           'INTROSPECTABLE_IFACE', 'PROPERTIES_IFACE',

           'ObjectPath', 'ByteArray', 'Signature', 'Byte', 'Boolean',
           'Int16', 'UInt16', 'Int32', 'UInt32', 'Int64', 'UInt64',
           'Double', 'String', 'Array', 'Struct', 'Dictionary',

           # from exceptions
           'DBusException',
           'MissingErrorHandlerException', 'MissingReplyHandlerException',
           'ValidationException', 'IntrospectionParserException',
           'UnknownMethodException', 'NameExistsException',

           # submodules
           'service', 'mainloop', 'lowlevel'
           ]

from dbus._compat import is_py2
if is_py2:
    __all__.append('UTF8String')

__docformat__ = 'restructuredtext'

# OLPC Sugar compatibility
import dbus.exceptions as exceptions
import dbus.types as types

from _dbus_bindings import __version__
version = tuple(map(int, __version__.split('.')))

from _dbus_bindings import (
    get_default_main_loop, set_default_main_loop, validate_bus_name,
    validate_error_name, validate_interface_name, validate_member_name,
    validate_object_path)
from _dbus_bindings import (
    BUS_DAEMON_IFACE, BUS_DAEMON_NAME, BUS_DAEMON_PATH, INTROSPECTABLE_IFACE,
    LOCAL_IFACE, LOCAL_PATH, PEER_IFACE, PROPERTIES_IFACE)

from dbus.exceptions import (
    DBusException, IntrospectionParserException, MissingErrorHandlerException,
    MissingReplyHandlerException, NameExistsException, UnknownMethodException,
    ValidationException)
from _dbus_bindings import (
    Array, Boolean, Byte, ByteArray, Dictionary, Double, Int16, Int32, Int64,
    ObjectPath, Signature, String, Struct, UInt16, UInt32, UInt64)

if is_py2:
    from _dbus_bindings import UTF8String

from dbus._dbus import Bus, SystemBus, SessionBus, StarterBus
from dbus.proxies import Interface
