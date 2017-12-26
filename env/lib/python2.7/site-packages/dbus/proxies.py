# Copyright (C) 2003-2007 Red Hat Inc. <http://www.redhat.com/>
# Copyright (C) 2003 David Zeuthen
# Copyright (C) 2004 Rob Taylor
# Copyright (C) 2005-2007 Collabora Ltd. <http://www.collabora.co.uk/>
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

import logging

try:
    from threading import RLock
except ImportError:
    from dummy_threading import RLock

import _dbus_bindings
from dbus._expat_introspect_parser import process_introspection_data
from dbus.exceptions import (
    DBusException, IntrospectionParserException, MissingErrorHandlerException,
    MissingReplyHandlerException)

__docformat__ = 'restructuredtext'


_logger = logging.getLogger('dbus.proxies')

from _dbus_bindings import (
    BUS_DAEMON_IFACE, BUS_DAEMON_NAME, BUS_DAEMON_PATH, INTROSPECTABLE_IFACE,
    LOCAL_PATH)
from dbus._compat import is_py2


class _DeferredMethod:
    """A proxy method which will only get called once we have its
    introspection reply.
    """
    def __init__(self, proxy_method, append, block):
        self._proxy_method = proxy_method
        # the test suite relies on the existence of this property
        self._method_name = proxy_method._method_name
        self._append = append
        self._block = block

    def __call__(self, *args, **keywords):
        if ('reply_handler' in keywords or
            keywords.get('ignore_reply', False)):
            # defer the async call til introspection finishes
            self._append(self._proxy_method, args, keywords)
            return None
        else:
            # we're being synchronous, so block
            self._block()
            return self._proxy_method(*args, **keywords)

    def call_async(self, *args, **keywords):
        self._append(self._proxy_method, args, keywords)


class _ProxyMethod:
    """A proxy method.

    Typically a member of a ProxyObject. Calls to the
    method produce messages that travel over the Bus and are routed
    to a specific named Service.
    """
    def __init__(self, proxy, connection, bus_name, object_path, method_name,
                 iface):
        if object_path == LOCAL_PATH:
            raise DBusException('Methods may not be called on the reserved '
                                'path %s' % LOCAL_PATH)

        # trust that the proxy, and the properties it had, are OK
        self._proxy          = proxy
        self._connection     = connection
        self._named_service  = bus_name
        self._object_path    = object_path
        # fail early if the method name is bad
        _dbus_bindings.validate_member_name(method_name)
        # the test suite relies on the existence of this property
        self._method_name    = method_name
        # fail early if the interface name is bad
        if iface is not None:
            _dbus_bindings.validate_interface_name(iface)
        self._dbus_interface = iface

    def __call__(self, *args, **keywords):
        reply_handler = keywords.pop('reply_handler', None)
        error_handler = keywords.pop('error_handler', None)
        ignore_reply = keywords.pop('ignore_reply', False)
        signature = keywords.pop('signature', None)

        if reply_handler is not None or error_handler is not None:
            if reply_handler is None:
                raise MissingReplyHandlerException()
            elif error_handler is None:
                raise MissingErrorHandlerException()
            elif ignore_reply:
                raise TypeError('ignore_reply and reply_handler cannot be '
                                'used together')

        dbus_interface = keywords.pop('dbus_interface', self._dbus_interface)

        if signature is None:
            if dbus_interface is None:
                key = self._method_name
            else:
                key = dbus_interface + '.' + self._method_name

            signature = self._proxy._introspect_method_map.get(key, None)

        if ignore_reply or reply_handler is not None:
            self._connection.call_async(self._named_service,
                                        self._object_path,
                                        dbus_interface,
                                        self._method_name,
                                        signature,
                                        args,
                                        reply_handler,
                                        error_handler,
                                        **keywords)
        else:
            return self._connection.call_blocking(self._named_service,
                                                  self._object_path,
                                                  dbus_interface,
                                                  self._method_name,
                                                  signature,
                                                  args,
                                                  **keywords)

    def call_async(self, *args, **keywords):
        reply_handler = keywords.pop('reply_handler', None)
        error_handler = keywords.pop('error_handler', None)
        signature = keywords.pop('signature', None)

        dbus_interface = keywords.pop('dbus_interface', self._dbus_interface)

        if signature is None:
            if dbus_interface:
                key = dbus_interface + '.' + self._method_name
            else:
                key = self._method_name
            signature = self._proxy._introspect_method_map.get(key, None)

        self._connection.call_async(self._named_service,
                                    self._object_path,
                                    dbus_interface,
                                    self._method_name,
                                    signature,
                                    args,
                                    reply_handler,
                                    error_handler,
                                    **keywords)


class ProxyObject(object):
    """A proxy to the remote Object.

    A ProxyObject is provided by the Bus. ProxyObjects
    have member functions, and can be called like normal Python objects.
    """
    ProxyMethodClass = _ProxyMethod
    DeferredMethodClass = _DeferredMethod

    INTROSPECT_STATE_DONT_INTROSPECT = 0
    INTROSPECT_STATE_INTROSPECT_IN_PROGRESS = 1
    INTROSPECT_STATE_INTROSPECT_DONE = 2

    def __init__(self, conn=None, bus_name=None, object_path=None,
                 introspect=True, follow_name_owner_changes=False, **kwargs):
        """Initialize the proxy object.

        :Parameters:
            `conn` : `dbus.connection.Connection`
                The bus or connection on which to find this object.
                The keyword argument `bus` is a deprecated alias for this.
            `bus_name` : str
                A bus name for the application owning the object, to be used
                as the destination for method calls and the sender for
                signal matches. The keyword argument ``named_service`` is a
                deprecated alias for this.
            `object_path` : str
                The object path at which the application exports the object
            `introspect` : bool
                If true (default), attempt to introspect the remote
                object to find out supported methods and their signatures
            `follow_name_owner_changes` : bool
                If true (default is false) and the `bus_name` is a
                well-known name, follow ownership changes for that name
        """
        bus = kwargs.pop('bus', None)
        if bus is not None:
            if conn is not None:
                raise TypeError('conn and bus cannot both be specified')
            conn = bus
            from warnings import warn
            warn('Passing the bus parameter to ProxyObject by name is '
                 'deprecated: please use positional parameters',
                 DeprecationWarning, stacklevel=2)
        named_service = kwargs.pop('named_service', None)
        if named_service is not None:
            if bus_name is not None:
                raise TypeError('bus_name and named_service cannot both be '
                                'specified')
            bus_name = named_service
            from warnings import warn
            warn('Passing the named_service parameter to ProxyObject by name '
                 'is deprecated: please use positional parameters',
                 DeprecationWarning, stacklevel=2)
        if kwargs:
            raise TypeError('ProxyObject.__init__ does not take these '
                            'keyword arguments: %s'
                            % ', '.join(kwargs.keys()))

        if follow_name_owner_changes:
            # we don't get the signals unless the Bus has a main loop
            # XXX: using Bus internals
            conn._require_main_loop()

        self._bus = conn

        if bus_name is not None:
            _dbus_bindings.validate_bus_name(bus_name)
        # the attribute is still called _named_service for the moment,
        # for the benefit of telepathy-python
        self._named_service = self._requested_bus_name = bus_name

        _dbus_bindings.validate_object_path(object_path)
        self.__dbus_object_path__ = object_path

        if not follow_name_owner_changes:
            self._named_service = conn.activate_name_owner(bus_name)

        #PendingCall object for Introspect call
        self._pending_introspect = None
        #queue of async calls waiting on the Introspect to return
        self._pending_introspect_queue = []
        #dictionary mapping method names to their input signatures
        self._introspect_method_map = {}

        # must be a recursive lock because block() is called while locked,
        # and calls the callback which re-takes the lock
        self._introspect_lock = RLock()

        if not introspect or self.__dbus_object_path__ == LOCAL_PATH:
            self._introspect_state = self.INTROSPECT_STATE_DONT_INTROSPECT
        else:
            self._introspect_state = self.INTROSPECT_STATE_INTROSPECT_IN_PROGRESS

            self._pending_introspect = self._Introspect()

    bus_name = property(lambda self: self._named_service, None, None,
            """The bus name to which this proxy is bound. (Read-only,
            may change.)

            If the proxy was instantiated using a unique name, this property
            is that unique name.

            If the proxy was instantiated with a well-known name and with
            ``follow_name_owner_changes`` set false (the default), this
            property is the unique name of the connection that owned that
            well-known name when the proxy was instantiated, which might
            not actually own the requested well-known name any more.

            If the proxy was instantiated with a well-known name and with
            ``follow_name_owner_changes`` set true, this property is that
            well-known name.
            """)

    requested_bus_name = property(lambda self: self._requested_bus_name,
            None, None,
            """The bus name which was requested when this proxy was
            instantiated.
            """)

    object_path = property(lambda self: self.__dbus_object_path__,
            None, None,
            """The object-path of this proxy.""")

    # XXX: We don't currently support this because it's the signal receiver
    # that's responsible for tracking name owner changes, but it
    # seems a natural thing to add in future.
    #unique_bus_name = property(lambda self: something, None, None,
    #        """The unique name of the connection to which this proxy is
    #        currently bound. (Read-only, may change.)
    #        """)

    def connect_to_signal(self, signal_name, handler_function, dbus_interface=None, **keywords):
        """Arrange for the given function to be called when the given signal
        is received.

        :Parameters:
            `signal_name` : str
                The name of the signal
            `handler_function` : callable
                A function to be called when the signal is emitted by
                the remote object. Its positional arguments will be the
                arguments of the signal; optionally, it may be given
                keyword arguments as described below.
            `dbus_interface` : str
                Optional interface with which to qualify the signal name.
                If None (the default) the handler will be called whenever a
                signal of the given member name is received, whatever
                its interface.
        :Keywords:
            `utf8_strings` : bool
                If True, the handler function will receive any string
                arguments as dbus.UTF8String objects (a subclass of str
                guaranteed to be UTF-8). If False (default) it will receive
                any string arguments as dbus.String objects (a subclass of
                unicode).
            `byte_arrays` : bool
                If True, the handler function will receive any byte-array
                arguments as dbus.ByteArray objects (a subclass of str).
                If False (default) it will receive any byte-array
                arguments as a dbus.Array of dbus.Byte (subclasses of:
                a list of ints).
            `sender_keyword` : str
                If not None (the default), the handler function will receive
                the unique name of the sending endpoint as a keyword
                argument with this name
            `destination_keyword` : str
                If not None (the default), the handler function will receive
                the bus name of the destination (or None if the signal is a
                broadcast, as is usual) as a keyword argument with this name.
            `interface_keyword` : str
                If not None (the default), the handler function will receive
                the signal interface as a keyword argument with this name.
            `member_keyword` : str
                If not None (the default), the handler function will receive
                the signal name as a keyword argument with this name.
            `path_keyword` : str
                If not None (the default), the handler function will receive
                the object-path of the sending object as a keyword argument
                with this name
            `message_keyword` : str
                If not None (the default), the handler function will receive
                the `dbus.lowlevel.SignalMessage` as a keyword argument with
                this name.
            `arg...` : unicode or UTF-8 str
                If there are additional keyword parameters of the form
                ``arg``\ *n*, match only signals where the *n*\ th argument
                is the value given for that keyword parameter. As of this time
                only string arguments can be matched (in particular,
                object paths and signatures can't).
        """
        return \
        self._bus.add_signal_receiver(handler_function,
                                      signal_name=signal_name,
                                      dbus_interface=dbus_interface,
                                      bus_name=self._named_service,
                                      path=self.__dbus_object_path__,
                                      **keywords)

    def _Introspect(self):
        kwargs = {}
        if is_py2:
            kwargs['utf8_strings'] = True
        return self._bus.call_async(self._named_service,
                                    self.__dbus_object_path__,
                                    INTROSPECTABLE_IFACE, 'Introspect', '', (),
                                    self._introspect_reply_handler,
                                    self._introspect_error_handler,
                                    require_main_loop=False, **kwargs)

    def _introspect_execute_queue(self):
        # FIXME: potential to flood the bus
        # We should make sure mainloops all have idle handlers
        # and do one message per idle
        for (proxy_method, args, keywords) in self._pending_introspect_queue:
            proxy_method(*args, **keywords)
        self._pending_introspect_queue = []

    def _introspect_reply_handler(self, data):
        self._introspect_lock.acquire()
        try:
            try:
                self._introspect_method_map = process_introspection_data(data)
            except IntrospectionParserException as e:
                self._introspect_error_handler(e)
                return

            self._introspect_state = self.INTROSPECT_STATE_INTROSPECT_DONE
            self._pending_introspect = None
            self._introspect_execute_queue()
        finally:
            self._introspect_lock.release()

    def _introspect_error_handler(self, error):
        logging.basicConfig()
        _logger.error("Introspect error on %s:%s: %s.%s: %s",
                      self._named_service, self.__dbus_object_path__,
                      error.__class__.__module__, error.__class__.__name__,
                      error)
        self._introspect_lock.acquire()
        try:
            _logger.debug('Executing introspect queue due to error')
            self._introspect_state = self.INTROSPECT_STATE_DONT_INTROSPECT
            self._pending_introspect = None
            self._introspect_execute_queue()
        finally:
            self._introspect_lock.release()

    def _introspect_block(self):
        self._introspect_lock.acquire()
        try:
            if self._pending_introspect is not None:
                self._pending_introspect.block()
            # else someone still has a _DeferredMethod from before we
            # finished introspection: no need to do anything special any more
        finally:
            self._introspect_lock.release()

    def _introspect_add_to_queue(self, callback, args, kwargs):
        self._introspect_lock.acquire()
        try:
            if self._introspect_state == self.INTROSPECT_STATE_INTROSPECT_IN_PROGRESS:
                self._pending_introspect_queue.append((callback, args, kwargs))
            else:
                # someone still has a _DeferredMethod from before we
                # finished introspection
                callback(*args, **kwargs)
        finally:
            self._introspect_lock.release()

    def __getattr__(self, member):
        if member.startswith('__') and member.endswith('__'):
            raise AttributeError(member)
        else:
            return self.get_dbus_method(member)

    def get_dbus_method(self, member, dbus_interface=None):
        """Return a proxy method representing the given D-Bus method. The
        returned proxy method can be called in the usual way. For instance, ::

            proxy.get_dbus_method("Foo", dbus_interface='com.example.Bar')(123)

        is equivalent to::

            proxy.Foo(123, dbus_interface='com.example.Bar')

        or even::

            getattr(proxy, "Foo")(123, dbus_interface='com.example.Bar')

        However, using `get_dbus_method` is the only way to call D-Bus
        methods with certain awkward names - if the author of a service
        implements a method called ``connect_to_signal`` or even
        ``__getattr__``, you'll need to use `get_dbus_method` to call them.

        For services which follow the D-Bus convention of CamelCaseMethodNames
        this won't be a problem.
        """

        ret = self.ProxyMethodClass(self, self._bus,
                                    self._named_service,
                                    self.__dbus_object_path__, member,
                                    dbus_interface)

        # this can be done without taking the lock - the worst that can
        # happen is that we accidentally return a _DeferredMethod just after
        # finishing introspection, in which case _introspect_add_to_queue and
        # _introspect_block will do the right thing anyway
        if self._introspect_state == self.INTROSPECT_STATE_INTROSPECT_IN_PROGRESS:
            ret = self.DeferredMethodClass(ret, self._introspect_add_to_queue,
                                           self._introspect_block)

        return ret

    def __repr__(self):
        return '<ProxyObject wrapping %s %s %s at %#x>'%(
            self._bus, self._named_service, self.__dbus_object_path__, id(self))
    __str__ = __repr__


class Interface(object):
    """An interface into a remote object.

    An Interface can be used to wrap ProxyObjects
    so that calls can be routed to their correct
    D-Bus interface.
    """

    def __init__(self, object, dbus_interface):
        """Construct a proxy for the given interface on the given object.

        :Parameters:
            `object` : `dbus.proxies.ProxyObject` or `dbus.Interface`
                The remote object or another of its interfaces
            `dbus_interface` : str
                An interface the `object` implements
        """
        if isinstance(object, Interface):
            self._obj = object.proxy_object
        else:
            self._obj = object
        self._dbus_interface = dbus_interface

    object_path = property (lambda self: self._obj.object_path, None, None,
                            "The D-Bus object path of the underlying object")
    __dbus_object_path__ = object_path
    bus_name = property (lambda self: self._obj.bus_name, None, None,
                         "The bus name to which the underlying proxy object "
                         "is bound")
    requested_bus_name = property (lambda self: self._obj.requested_bus_name,
                                   None, None,
                                   "The bus name which was requested when the "
                                   "underlying object was created")
    proxy_object = property (lambda self: self._obj, None, None,
                             """The underlying proxy object""")
    dbus_interface = property (lambda self: self._dbus_interface, None, None,
                               """The D-Bus interface represented""")

    def connect_to_signal(self, signal_name, handler_function,
                          dbus_interface=None, **keywords):
        """Arrange for a function to be called when the given signal is
        emitted.

        The parameters and keyword arguments are the same as for
        `dbus.proxies.ProxyObject.connect_to_signal`, except that if
        `dbus_interface` is None (the default), the D-Bus interface that
        was passed to the `Interface` constructor is used.
        """
        if not dbus_interface:
            dbus_interface = self._dbus_interface

        return self._obj.connect_to_signal(signal_name, handler_function,
                                           dbus_interface, **keywords)

    def __getattr__(self, member):
        if member.startswith('__') and member.endswith('__'):
            raise AttributeError(member)
        else:
            return self._obj.get_dbus_method(member, self._dbus_interface)

    def get_dbus_method(self, member, dbus_interface=None):
        """Return a proxy method representing the given D-Bus method.

        This is the same as `dbus.proxies.ProxyObject.get_dbus_method`
        except that if `dbus_interface` is None (the default),
        the D-Bus interface that was passed to the `Interface` constructor
        is used.
        """
        if dbus_interface is None:
            dbus_interface = self._dbus_interface
        return self._obj.get_dbus_method(member, dbus_interface)

    def __repr__(self):
        return '<Interface %r implementing %r at %#x>'%(
        self._obj, self._dbus_interface, id(self))
    __str__ = __repr__
