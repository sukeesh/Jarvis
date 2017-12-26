"""Implementation for dbus.Bus. Not to be imported directly."""

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

from __future__ import generators

__all__ = ('Bus', 'SystemBus', 'SessionBus', 'StarterBus')
__docformat__ = 'reStructuredText'

from dbus.exceptions import DBusException
from _dbus_bindings import (
    BUS_DAEMON_IFACE, BUS_DAEMON_NAME, BUS_DAEMON_PATH, BUS_SESSION,
    BUS_STARTER, BUS_SYSTEM, DBUS_START_REPLY_ALREADY_RUNNING,
    DBUS_START_REPLY_SUCCESS, validate_bus_name,
    validate_interface_name, validate_member_name, validate_object_path)
from dbus.bus import BusConnection
from dbus.lowlevel import SignalMessage
from dbus._compat import is_py2

if is_py2:
    from _dbus_bindings import UTF8String


class Bus(BusConnection):
    """A connection to one of three possible standard buses, the SESSION,
    SYSTEM, or STARTER bus. This class manages shared connections to those
    buses.

    If you're trying to subclass `Bus`, you may be better off subclassing
    `BusConnection`, which doesn't have all this magic.
    """

    _shared_instances = {}

    def __new__(cls, bus_type=BusConnection.TYPE_SESSION, private=False,
                mainloop=None):
        """Constructor, returning an existing instance where appropriate.

        The returned instance is actually always an instance of `SessionBus`,
        `SystemBus` or `StarterBus`.

        :Parameters:
            `bus_type` : cls.TYPE_SESSION, cls.TYPE_SYSTEM or cls.TYPE_STARTER
                Connect to the appropriate bus
            `private` : bool
                If true, never return an existing shared instance, but instead
                return a private connection.

                :Deprecated: since 0.82.3. Use dbus.bus.BusConnection for
                    private connections.

            `mainloop` : dbus.mainloop.NativeMainLoop
                The main loop to use. The default is to use the default
                main loop if one has been set up, or raise an exception
                if none has been.
        :Changed: in dbus-python 0.80:
            converted from a wrapper around a Connection to a Connection
            subclass.
        """
        if (not private and bus_type in cls._shared_instances):
            return cls._shared_instances[bus_type]

        # this is a bit odd, but we create instances of the subtypes
        # so we can return the shared instances if someone tries to
        # construct one of them (otherwise we'd eg try and return an
        # instance of Bus from __new__ in SessionBus). why are there
        # three ways to construct this class? we just don't know.
        if bus_type == BUS_SESSION:
            subclass = SessionBus
        elif bus_type == BUS_SYSTEM:
            subclass = SystemBus
        elif bus_type == BUS_STARTER:
            subclass = StarterBus
        else:
            raise ValueError('invalid bus_type %s' % bus_type)

        bus = BusConnection.__new__(subclass, bus_type, mainloop=mainloop)

        bus._bus_type = bus_type

        if not private:
            cls._shared_instances[bus_type] = bus

        return bus

    def close(self):
        t = self._bus_type
        if self.__class__._shared_instances.get(t) is self:
            del self.__class__._shared_instances[t]
        super(Bus, self).close()

    def get_connection(self):
        """Return self, for backwards compatibility with earlier dbus-python
        versions where Bus was not a subclass of Connection.

        :Deprecated: since 0.80.0
        """
        return self
    _connection = property(get_connection, None, None,
                           """self._connection == self, for backwards
                           compatibility with earlier dbus-python versions
                           where Bus was not a subclass of Connection.""")

    def get_session(private=False):
        """Static method that returns a connection to the session bus.

        :Parameters:
            `private` : bool
                If true, do not return a shared connection.
        """
        return SessionBus(private=private)

    get_session = staticmethod(get_session)

    def get_system(private=False):
        """Static method that returns a connection to the system bus.

        :Parameters:
            `private` : bool
                If true, do not return a shared connection.
        """
        return SystemBus(private=private)

    get_system = staticmethod(get_system)


    def get_starter(private=False):
        """Static method that returns a connection to the starter bus.

        :Parameters:
            `private` : bool
                If true, do not return a shared connection.
        """
        return StarterBus(private=private)

    get_starter = staticmethod(get_starter)

    def __repr__(self):
        if self._bus_type == BUS_SESSION:
            name = 'session'
        elif self._bus_type == BUS_SYSTEM:
            name = 'system'
        elif self._bus_type == BUS_STARTER:
            name = 'starter'
        else:
            name = 'unknown bus type'

        return '<%s.%s (%s) at %#x>' % (self.__class__.__module__,
                                        self.__class__.__name__,
                                        name, id(self))
    __str__ = __repr__


# FIXME: Drop the subclasses here? I can't think why we'd ever want
# polymorphism
class SystemBus(Bus):
    """The system-wide message bus."""
    def __new__(cls, private=False, mainloop=None):
        """Return a connection to the system bus.

        :Parameters:
            `private` : bool
                If true, never return an existing shared instance, but instead
                return a private connection.
            `mainloop` : dbus.mainloop.NativeMainLoop
                The main loop to use. The default is to use the default
                main loop if one has been set up, or raise an exception
                if none has been.
        """
        return Bus.__new__(cls, Bus.TYPE_SYSTEM, mainloop=mainloop,
                           private=private)

class SessionBus(Bus):
    """The session (current login) message bus."""
    def __new__(cls, private=False, mainloop=None):
        """Return a connection to the session bus.

        :Parameters:
            `private` : bool
                If true, never return an existing shared instance, but instead
                return a private connection.
            `mainloop` : dbus.mainloop.NativeMainLoop
                The main loop to use. The default is to use the default
                main loop if one has been set up, or raise an exception
                if none has been.
        """
        return Bus.__new__(cls, Bus.TYPE_SESSION, private=private,
                           mainloop=mainloop)

class StarterBus(Bus):
    """The bus that activated this process (only valid if
    this process was launched by DBus activation).
    """
    def __new__(cls, private=False, mainloop=None):
        """Return a connection to the bus that activated this process.

        :Parameters:
            `private` : bool
                If true, never return an existing shared instance, but instead
                return a private connection.
            `mainloop` : dbus.mainloop.NativeMainLoop
                The main loop to use. The default is to use the default
                main loop if one has been set up, or raise an exception
                if none has been.
        """
        return Bus.__new__(cls, Bus.TYPE_STARTER, private=private,
                           mainloop=mainloop)
