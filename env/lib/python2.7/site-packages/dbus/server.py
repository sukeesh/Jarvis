# Copyright (C) 2008 Openismus GmbH <http://openismus.com/>
# Copyright (C) 2008 Collabora Ltd. <http://www.collabora.co.uk/>
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

__all__ = ('Server', )
__docformat__ = 'reStructuredText'

from _dbus_bindings import _Server
from dbus.connection import Connection

class Server(_Server):
    """An opaque object representing a server that listens for connections from
    other applications.

    This class is not useful to instantiate directly: you must subclass it and
    either extend the method connection_added, or append to the
    list on_connection_added.

    :Since: 0.83
    """

    def __new__(cls, address, connection_class=Connection,
        mainloop=None, auth_mechanisms=None):
        """Construct a new Server.

        :Parameters:
            `address` : str
                Listen on this address.
            `connection_class` : type
                When new connections come in, instantiate this subclass
                of dbus.connection.Connection to represent them.
                The default is Connection.
            `mainloop` : dbus.mainloop.NativeMainLoop or None
                The main loop with which to associate the new connections.
            `auth_mechanisms` : sequence of str
                Authentication mechanisms to allow. The default is to allow
                any authentication mechanism supported by ``libdbus``.
        """
        return super(Server, cls).__new__(cls, address, connection_class,
                mainloop, auth_mechanisms)

    def __init__(self, *args, **kwargs):

        self.__connections = {}

        self.on_connection_added = []
        """A list of callbacks to invoke when a connection is added.
        They receive two arguments: this Server and the new Connection."""

        self.on_connection_removed = []
        """A list of callbacks to invoke when a connection becomes
        disconnected. They receive two arguments: this Server and the removed
        Connection."""

    # This method name is hard-coded in _dbus_bindings._Server.
    # This is not public API.
    def _on_new_connection(self, conn):
        conn.call_on_disconnection(self.connection_removed)
        self.connection_added(conn)

    def connection_added(self, conn):
        """Respond to the creation of a new Connection.

        This base-class implementation just invokes the callbacks in
        the on_connection_added attribute.

        :Parameters:
            `conn` : dbus.connection.Connection
                A D-Bus connection which has just been added.

                The type of this parameter is whatever was passed
                to the Server constructor as the ``connection_class``.
        """
        if self.on_connection_added:
            for cb in self.on_connection_added:
                cb(conn)

    def connection_removed(self, conn):
        """Respond to the disconnection of a Connection.

        This base-class implementation just invokes the callbacks in
        the on_connection_removed attribute.

        :Parameters:
            `conn` : dbus.connection.Connection
                A D-Bus connection which has just become disconnected.

                The type of this parameter is whatever was passed
                to the Server constructor as the ``connection_class``.
        """
        if self.on_connection_removed:
            for cb in self.on_connection_removed:
                cb(conn)

    address      = property(_Server.get_address)
    id           = property(_Server.get_id)
    is_connected = property(_Server.get_is_connected)

