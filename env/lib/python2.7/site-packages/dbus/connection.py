# Copyright (C) 2007 Collabora Ltd. <http://www.collabora.co.uk/>
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

__all__ = ('Connection', 'SignalMatch')
__docformat__ = 'reStructuredText'

import logging
import threading
import weakref

from _dbus_bindings import (
    Connection as _Connection, LOCAL_IFACE, LOCAL_PATH, validate_bus_name,
    validate_interface_name, validate_member_name, validate_object_path)
from dbus.exceptions import DBusException
from dbus.lowlevel import (
    ErrorMessage, HANDLER_RESULT_NOT_YET_HANDLED, MethodCallMessage,
    MethodReturnMessage, SignalMessage)
from dbus.proxies import ProxyObject
from dbus._compat import is_py2, is_py3

if is_py3:
    from _dbus_bindings import String
else:
    from _dbus_bindings import UTF8String


_logger = logging.getLogger('dbus.connection')


def _noop(*args, **kwargs):
    pass


class SignalMatch(object):
    _slots = ['_sender_name_owner', '_member', '_interface', '_sender',
              '_path', '_handler', '_args_match', '_rule',
              '_byte_arrays', '_conn_weakref',
              '_destination_keyword', '_interface_keyword',
              '_message_keyword', '_member_keyword',
              '_sender_keyword', '_path_keyword', '_int_args_match']
    if is_py2:
        _slots.append('_utf8_strings')

    __slots__ = tuple(_slots)

    def __init__(self, conn, sender, object_path, dbus_interface,
                 member, handler, byte_arrays=False,
                 sender_keyword=None, path_keyword=None,
                 interface_keyword=None, member_keyword=None,
                 message_keyword=None, destination_keyword=None,
                 **kwargs):
        if member is not None:
            validate_member_name(member)
        if dbus_interface is not None:
            validate_interface_name(dbus_interface)
        if sender is not None:
            validate_bus_name(sender)
        if object_path is not None:
            validate_object_path(object_path)

        self._rule = None
        self._conn_weakref = weakref.ref(conn)
        self._sender = sender
        self._interface = dbus_interface
        self._member = member
        self._path = object_path
        self._handler = handler

        # if the connection is actually a bus, it's responsible for changing
        # this later
        self._sender_name_owner = sender

        if is_py2:
            self._utf8_strings = kwargs.pop('utf8_strings', False)
        elif 'utf8_strings' in kwargs:
            raise TypeError("unexpected keyword argument 'utf8_strings'")

        self._byte_arrays = byte_arrays
        self._sender_keyword = sender_keyword
        self._path_keyword = path_keyword
        self._member_keyword = member_keyword
        self._interface_keyword = interface_keyword
        self._message_keyword = message_keyword
        self._destination_keyword = destination_keyword

        self._args_match = kwargs
        if not kwargs:
            self._int_args_match = None
        else:
            self._int_args_match = {}
            for kwarg in kwargs:
                if not kwarg.startswith('arg'):
                    raise TypeError('SignalMatch: unknown keyword argument %s'
                                    % kwarg)
                try:
                    index = int(kwarg[3:])
                except ValueError:
                    raise TypeError('SignalMatch: unknown keyword argument %s'
                                    % kwarg)
                if index < 0 or index > 63:
                    raise TypeError('SignalMatch: arg match index must be in '
                                    'range(64), not %d' % index)
                self._int_args_match[index] = kwargs[kwarg]

    def __hash__(self):
        """SignalMatch objects are compared by identity."""
        return hash(id(self))

    def __eq__(self, other):
        """SignalMatch objects are compared by identity."""
        return self is other

    def __ne__(self, other):
        """SignalMatch objects are compared by identity."""
        return self is not other

    sender = property(lambda self: self._sender)

    def __str__(self):
        if self._rule is None:
            rule = ["type='signal'"]
            if self._sender is not None:
                rule.append("sender='%s'" % self._sender)
            if self._path is not None:
                rule.append("path='%s'" % self._path)
            if self._interface is not None:
                rule.append("interface='%s'" % self._interface)
            if self._member is not None:
                rule.append("member='%s'" % self._member)
            if self._int_args_match is not None:
                for index, value in self._int_args_match.items():
                    rule.append("arg%d='%s'" % (index, value))

            self._rule = ','.join(rule)

        return self._rule

    def __repr__(self):
        return ('<%s at %x "%s" on conn %r>'
                % (self.__class__, id(self), self._rule, self._conn_weakref()))

    def set_sender_name_owner(self, new_name):
        self._sender_name_owner = new_name

    def matches_removal_spec(self, sender, object_path,
                             dbus_interface, member, handler, **kwargs):
        if handler not in (None, self._handler):
            return False
        if sender != self._sender:
            return False
        if object_path != self._path:
            return False
        if dbus_interface != self._interface:
            return False
        if member != self._member:
            return False
        if kwargs != self._args_match:
            return False
        return True

    def maybe_handle_message(self, message):
        args = None

        # these haven't been checked yet by the match tree
        if self._sender_name_owner not in (None, message.get_sender()):
            return False
        if self._int_args_match is not None:
            # extracting args with utf8_strings and byte_arrays is less work
            kwargs = dict(byte_arrays=True)
            arg_type = (String if is_py3 else UTF8String)
            if is_py2:
                kwargs['utf8_strings'] = True
            args = message.get_args_list(**kwargs)
            for index, value in self._int_args_match.items():
                if (index >= len(args)
                    or not isinstance(args[index], arg_type)
                    or args[index] != value):
                    return False

        # these have likely already been checked by the match tree
        if self._member not in (None, message.get_member()):
            return False
        if self._interface not in (None, message.get_interface()):
            return False
        if self._path not in (None, message.get_path()):
            return False

        try:
            # minor optimization: if we already extracted the args with the
            # right calling convention to do the args match, don't bother
            # doing so again
            utf8_strings = (is_py2 and self._utf8_strings)
            if args is None or not utf8_strings or not self._byte_arrays:
                kwargs = dict(byte_arrays=self._byte_arrays)
                if is_py2:
                    kwargs['utf8_strings'] = self._utf8_strings
                args = message.get_args_list(**kwargs)
            kwargs = {}
            if self._sender_keyword is not None:
                kwargs[self._sender_keyword] = message.get_sender()
            if self._destination_keyword is not None:
                kwargs[self._destination_keyword] = message.get_destination()
            if self._path_keyword is not None:
                kwargs[self._path_keyword] = message.get_path()
            if self._member_keyword is not None:
                kwargs[self._member_keyword] = message.get_member()
            if self._interface_keyword is not None:
                kwargs[self._interface_keyword] = message.get_interface()
            if self._message_keyword is not None:
                kwargs[self._message_keyword] = message
            self._handler(*args, **kwargs)
        except:
            # basicConfig is a no-op if logging is already configured
            logging.basicConfig()
            _logger.error('Exception in handler for D-Bus signal:', exc_info=1)

        return True

    def remove(self):
        conn = self._conn_weakref()
        # do nothing if the connection has already vanished
        if conn is not None:
            conn.remove_signal_receiver(self, self._member,
                                        self._interface, self._sender,
                                        self._path,
                                        **self._args_match)


class Connection(_Connection):
    """A connection to another application. In this base class there is
    assumed to be no bus daemon.

    :Since: 0.81.0
    """

    ProxyObjectClass = ProxyObject

    def __init__(self, *args, **kwargs):
        super(Connection, self).__init__(*args, **kwargs)

        # this if-block is needed because shared bus connections can be
        # __init__'ed more than once
        if not hasattr(self, '_dbus_Connection_initialized'):
            self._dbus_Connection_initialized = 1

            self.__call_on_disconnection = []

            self._signal_recipients_by_object_path = {}
            """Map from object path to dict mapping dbus_interface to dict
            mapping member to list of SignalMatch objects."""

            self._signals_lock = threading.Lock()
            """Lock used to protect signal data structures"""

            self.add_message_filter(self.__class__._signal_func)

    def activate_name_owner(self, bus_name):
        """Return the unique name for the given bus name, activating it
        if necessary and possible.

        If the name is already unique or this connection is not to a
        bus daemon, just return it.

        :Returns: a bus name. If the given `bus_name` exists, the returned
            name identifies its current owner; otherwise the returned name
            does not exist.
        :Raises DBusException: if the implementation has failed
            to activate the given bus name.
        :Since: 0.81.0
        """
        return bus_name

    def get_object(self, bus_name=None, object_path=None, introspect=True,
                   **kwargs):
        """Return a local proxy for the given remote object.

        Method calls on the proxy are translated into method calls on the
        remote object.

        :Parameters:
            `bus_name` : str
                A bus name (either the unique name or a well-known name)
                of the application owning the object. The keyword argument
                named_service is a deprecated alias for this.
            `object_path` : str
                The object path of the desired object
            `introspect` : bool
                If true (default), attempt to introspect the remote
                object to find out supported methods and their signatures

        :Returns: a `dbus.proxies.ProxyObject`
        """
        named_service = kwargs.pop('named_service', None)
        if named_service is not None:
            if bus_name is not None:
                raise TypeError('bus_name and named_service cannot both '
                                'be specified')
            from warnings import warn
            warn('Passing the named_service parameter to get_object by name '
                 'is deprecated: please use positional parameters',
                 DeprecationWarning, stacklevel=2)
            bus_name = named_service
        if kwargs:
            raise TypeError('get_object does not take these keyword '
                            'arguments: %s' % ', '.join(kwargs.keys()))

        return self.ProxyObjectClass(self, bus_name, object_path,
                                     introspect=introspect)

    def add_signal_receiver(self, handler_function,
                                  signal_name=None,
                                  dbus_interface=None,
                                  bus_name=None,
                                  path=None,
                                  **keywords):
        """Arrange for the given function to be called when a signal matching
        the parameters is received.

        :Parameters:
            `handler_function` : callable
                The function to be called. Its positional arguments will
                be the arguments of the signal. By default it will receive
                no keyword arguments, but see the description of
                the optional keyword arguments below.
            `signal_name` : str
                The signal name; None (the default) matches all names
            `dbus_interface` : str
                The D-Bus interface name with which to qualify the signal;
                None (the default) matches all interface names
            `bus_name` : str
                A bus name for the sender, which will be resolved to a
                unique name if it is not already; None (the default) matches
                any sender.
            `path` : str
                The object path of the object which must have emitted the
                signal; None (the default) matches any object path
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
                argument with this name.
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
                with this name.
            `message_keyword` : str
                If not None (the default), the handler function will receive
                the `dbus.lowlevel.SignalMessage` as a keyword argument with
                this name.
            `arg...` : unicode or UTF-8 str
                If there are additional keyword parameters of the form
                ``arg``\ *n*, match only signals where the *n*\ th argument
                is the value given for that keyword parameter. As of this
                time only string arguments can be matched (in particular,
                object paths and signatures can't).
            `named_service` : str
                A deprecated alias for `bus_name`.
        """
        self._require_main_loop()

        named_service = keywords.pop('named_service', None)
        if named_service is not None:
            if bus_name is not None:
                raise TypeError('bus_name and named_service cannot both be '
                                'specified')
            bus_name = named_service
            from warnings import warn
            warn('Passing the named_service parameter to add_signal_receiver '
                 'by name is deprecated: please use positional parameters',
                 DeprecationWarning, stacklevel=2)

        match = SignalMatch(self, bus_name, path, dbus_interface,
                            signal_name, handler_function, **keywords)

        self._signals_lock.acquire()
        try:
            by_interface = self._signal_recipients_by_object_path.setdefault(
                    path, {})
            by_member = by_interface.setdefault(dbus_interface, {})
            matches = by_member.setdefault(signal_name, [])

            matches.append(match)
        finally:
            self._signals_lock.release()

        return match

    def _iter_easy_matches(self, path, dbus_interface, member):
        if path is not None:
            path_keys = (None, path)
        else:
            path_keys = (None,)
        if dbus_interface is not None:
            interface_keys = (None, dbus_interface)
        else:
            interface_keys = (None,)
        if member is not None:
            member_keys = (None, member)
        else:
            member_keys = (None,)

        for path in path_keys:
            by_interface = self._signal_recipients_by_object_path.get(path)
            if by_interface is None:
                continue
            for dbus_interface in interface_keys:
                by_member = by_interface.get(dbus_interface, None)
                if by_member is None:
                    continue
                for member in member_keys:
                    matches = by_member.get(member, None)
                    if matches is None:
                        continue
                    for m in matches:
                        yield m

    def remove_signal_receiver(self, handler_or_match,
                               signal_name=None,
                               dbus_interface=None,
                               bus_name=None,
                               path=None,
                               **keywords):
        named_service = keywords.pop('named_service', None)
        if named_service is not None:
            if bus_name is not None:
                raise TypeError('bus_name and named_service cannot both be '
                                'specified')
            bus_name = named_service
            from warnings import warn
            warn('Passing the named_service parameter to '
                 'remove_signal_receiver by name is deprecated: please use '
                 'positional parameters',
                 DeprecationWarning, stacklevel=2)

        new = []
        deletions = []
        self._signals_lock.acquire()
        try:
            by_interface = self._signal_recipients_by_object_path.get(path,
                                                                      None)
            if by_interface is None:
                return
            by_member = by_interface.get(dbus_interface, None)
            if by_member is None:
                return
            matches = by_member.get(signal_name, None)
            if matches is None:
                return

            for match in matches:
                if (handler_or_match is match
                    or match.matches_removal_spec(bus_name,
                                                  path,
                                                  dbus_interface,
                                                  signal_name,
                                                  handler_or_match,
                                                  **keywords)):
                    deletions.append(match)
                else:
                    new.append(match)

            if new:
                by_member[signal_name] = new
            else:
                del by_member[signal_name]
                if not by_member:
                    del by_interface[dbus_interface]
                    if not by_interface:
                        del self._signal_recipients_by_object_path[path]
        finally:
            self._signals_lock.release()

        for match in deletions:
            self._clean_up_signal_match(match)

    def _clean_up_signal_match(self, match):
        # Now called without the signals lock held (it was held in <= 0.81.0)
        pass

    def _signal_func(self, message):
        """D-Bus filter function. Handle signals by dispatching to Python
        callbacks kept in the match-rule tree.
        """

        if not isinstance(message, SignalMessage):
            return HANDLER_RESULT_NOT_YET_HANDLED

        dbus_interface = message.get_interface()
        path = message.get_path()
        signal_name = message.get_member()

        for match in self._iter_easy_matches(path, dbus_interface,
                                             signal_name):
            match.maybe_handle_message(message)

        if (dbus_interface == LOCAL_IFACE and
            path == LOCAL_PATH and
            signal_name == 'Disconnected'):
            for cb in self.__call_on_disconnection:
                try:
                    cb(self)
                except Exception:
                    # basicConfig is a no-op if logging is already configured
                    logging.basicConfig()
                    _logger.error('Exception in handler for Disconnected '
                        'signal:', exc_info=1)

        return HANDLER_RESULT_NOT_YET_HANDLED

    def call_async(self, bus_name, object_path, dbus_interface, method,
                   signature, args, reply_handler, error_handler,
                   timeout=-1.0, byte_arrays=False,
                   require_main_loop=True, **kwargs):
        """Call the given method, asynchronously.

        If the reply_handler is None, successful replies will be ignored.
        If the error_handler is None, failures will be ignored. If both
        are None, the implementation may request that no reply is sent.

        :Returns: The dbus.lowlevel.PendingCall.
        :Since: 0.81.0
        """
        if object_path == LOCAL_PATH:
            raise DBusException('Methods may not be called on the reserved '
                                'path %s' % LOCAL_PATH)
        if dbus_interface == LOCAL_IFACE:
            raise DBusException('Methods may not be called on the reserved '
                                'interface %s' % LOCAL_IFACE)
        # no need to validate other args - MethodCallMessage ctor will do

        get_args_opts = dict(byte_arrays=byte_arrays)
        if is_py2:
            get_args_opts['utf8_strings'] = kwargs.get('utf8_strings', False)
        elif 'utf8_strings' in kwargs:
            raise TypeError("unexpected keyword argument 'utf8_strings'")

        message = MethodCallMessage(destination=bus_name,
                                    path=object_path,
                                    interface=dbus_interface,
                                    method=method)
        # Add the arguments to the function
        try:
            message.append(signature=signature, *args)
        except Exception as e:
            logging.basicConfig()
            _logger.error('Unable to set arguments %r according to '
                          'signature %r: %s: %s',
                          args, signature, e.__class__, e)
            raise

        if reply_handler is None and error_handler is None:
            # we don't care what happens, so just send it
            self.send_message(message)
            return

        if reply_handler is None:
            reply_handler = _noop
        if error_handler is None:
            error_handler = _noop

        def msg_reply_handler(message):
            if isinstance(message, MethodReturnMessage):
                reply_handler(*message.get_args_list(**get_args_opts))
            elif isinstance(message, ErrorMessage):
                error_handler(DBusException(name=message.get_error_name(),
                                            *message.get_args_list()))
            else:
                error_handler(TypeError('Unexpected type for reply '
                                        'message: %r' % message))
        return self.send_message_with_reply(message, msg_reply_handler,
                                        timeout,
                                        require_main_loop=require_main_loop)

    def call_blocking(self, bus_name, object_path, dbus_interface, method,
                      signature, args, timeout=-1.0,
                      byte_arrays=False, **kwargs):
        """Call the given method, synchronously.
        :Since: 0.81.0
        """
        if object_path == LOCAL_PATH:
            raise DBusException('Methods may not be called on the reserved '
                                'path %s' % LOCAL_PATH)
        if dbus_interface == LOCAL_IFACE:
            raise DBusException('Methods may not be called on the reserved '
                                'interface %s' % LOCAL_IFACE)
        # no need to validate other args - MethodCallMessage ctor will do

        get_args_opts = dict(byte_arrays=byte_arrays)
        if is_py2:
            get_args_opts['utf8_strings'] = kwargs.get('utf8_strings', False)
        elif 'utf8_strings' in kwargs:
            raise TypeError("unexpected keyword argument 'utf8_strings'")

        message = MethodCallMessage(destination=bus_name,
                                    path=object_path,
                                    interface=dbus_interface,
                                    method=method)
        # Add the arguments to the function
        try:
            message.append(signature=signature, *args)
        except Exception as e:
            logging.basicConfig()
            _logger.error('Unable to set arguments %r according to '
                          'signature %r: %s: %s',
                          args, signature, e.__class__, e)
            raise

        # make a blocking call
        reply_message = self.send_message_with_reply_and_block(
            message, timeout)
        args_list = reply_message.get_args_list(**get_args_opts)
        if len(args_list) == 0:
            return None
        elif len(args_list) == 1:
            return args_list[0]
        else:
            return tuple(args_list)

    def call_on_disconnection(self, callable):
        """Arrange for `callable` to be called with one argument (this
        Connection object) when the Connection becomes
        disconnected.

        :Since: 0.83.0
        """
        self.__call_on_disconnection.append(callable)
