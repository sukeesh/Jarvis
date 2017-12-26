"""Service-side D-Bus decorators."""

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

__all__ = ('method', 'signal')
__docformat__ = 'restructuredtext'

import inspect

from dbus import validate_interface_name, Signature, validate_member_name
from dbus.lowlevel import SignalMessage
from dbus.exceptions import DBusException
from dbus._compat import is_py2


def method(dbus_interface, in_signature=None, out_signature=None,
           async_callbacks=None,
           sender_keyword=None, path_keyword=None, destination_keyword=None,
           message_keyword=None, connection_keyword=None,
           byte_arrays=False,
           rel_path_keyword=None, **kwargs):
    """Factory for decorators used to mark methods of a `dbus.service.Object`
    to be exported on the D-Bus.

    The decorated method will be exported over D-Bus as the method of the
    same name on the given D-Bus interface.

    :Parameters:
        `dbus_interface` : str
            Name of a D-Bus interface
        `in_signature` : str or None
            If not None, the signature of the method parameters in the usual
            D-Bus notation
        `out_signature` : str or None
            If not None, the signature of the return value in the usual
            D-Bus notation
        `async_callbacks` : tuple containing (str,str), or None
            If None (default) the decorated method is expected to return
            values matching the `out_signature` as usual, or raise
            an exception on error. If not None, the following applies:

            `async_callbacks` contains the names of two keyword arguments to
            the decorated function, which will be used to provide a success
            callback and an error callback (in that order).

            When the decorated method is called via the D-Bus, its normal
            return value will be ignored; instead, a pair of callbacks are
            passed as keyword arguments, and the decorated method is
            expected to arrange for one of them to be called.

            On success the success callback must be called, passing the
            results of this method as positional parameters in the format
            given by the `out_signature`.

            On error the decorated method may either raise an exception
            before it returns, or arrange for the error callback to be
            called with an Exception instance as parameter.

        `sender_keyword` : str or None
            If not None, contains the name of a keyword argument to the
            decorated function, conventionally ``'sender'``. When the
            method is called, the sender's unique name will be passed as
            this keyword argument.

        `path_keyword` : str or None
            If not None (the default), the decorated method will receive
            the destination object path as a keyword argument with this
            name. Normally you already know the object path, but in the
            case of "fallback paths" you'll usually want to use the object
            path in the method's implementation.

            For fallback objects, `rel_path_keyword` (new in 0.82.2) is
            likely to be more useful.

            :Since: 0.80.0?

        `rel_path_keyword` : str or None
            If not None (the default), the decorated method will receive
            the destination object path, relative to the path at which the
            object was exported, as a keyword argument with this
            name. For non-fallback objects the relative path will always be
            '/'.

            :Since: 0.82.2

        `destination_keyword` : str or None
            If not None (the default), the decorated method will receive
            the destination bus name as a keyword argument with this name.
            Included for completeness - you shouldn't need this.

            :Since: 0.80.0?

        `message_keyword` : str or None
            If not None (the default), the decorated method will receive
            the `dbus.lowlevel.MethodCallMessage` as a keyword argument
            with this name.

            :Since: 0.80.0?

        `connection_keyword` : str or None
            If not None (the default), the decorated method will receive
            the `dbus.connection.Connection` as a keyword argument
            with this name. This is generally only useful for objects
            that are available on more than one connection.

            :Since: 0.82.0

        `utf8_strings` : bool
            If False (default), D-Bus strings are passed to the decorated
            method as objects of class dbus.String, a unicode subclass.

            If True, D-Bus strings are passed to the decorated method
            as objects of class dbus.UTF8String, a str subclass guaranteed
            to be encoded in UTF-8.

            This option does not affect object-paths and signatures, which
            are always 8-bit strings (str subclass) encoded in ASCII.

            :Since: 0.80.0

        `byte_arrays` : bool
            If False (default), a byte array will be passed to the decorated
            method as an `Array` (a list subclass) of `Byte` objects.

            If True, a byte array will be passed to the decorated method as
            a `ByteArray`, a str subclass. This is usually what you want,
            but is switched off by default to keep dbus-python's API
            consistent.

            :Since: 0.80.0
    """
    validate_interface_name(dbus_interface)

    def decorator(func):
        if hasattr(inspect, 'Signature'):
            args = []

            for arg in inspect.signature(func).parameters.values():
                if arg.kind in (inspect.Parameter.POSITIONAL_ONLY,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD):
                    args.append(arg.name)
        else:
            args = inspect.getargspec(func)[0]

        args.pop(0)

        if async_callbacks:
            if type(async_callbacks) != tuple:
                raise TypeError('async_callbacks must be a tuple of (keyword for return callback, keyword for error callback)')
            if len(async_callbacks) != 2:
                raise ValueError('async_callbacks must be a tuple of (keyword for return callback, keyword for error callback)')
            args.remove(async_callbacks[0])
            args.remove(async_callbacks[1])

        if sender_keyword:
            args.remove(sender_keyword)
        if rel_path_keyword:
            args.remove(rel_path_keyword)
        if path_keyword:
            args.remove(path_keyword)
        if destination_keyword:
            args.remove(destination_keyword)
        if message_keyword:
            args.remove(message_keyword)
        if connection_keyword:
            args.remove(connection_keyword)

        if in_signature:
            in_sig = tuple(Signature(in_signature))

            if len(in_sig) > len(args):
                raise ValueError('input signature is longer than the number of arguments taken')
            elif len(in_sig) < len(args):
                raise ValueError('input signature is shorter than the number of arguments taken')

        func._dbus_is_method = True
        func._dbus_async_callbacks = async_callbacks
        func._dbus_interface = dbus_interface
        func._dbus_in_signature = in_signature
        func._dbus_out_signature = out_signature
        func._dbus_sender_keyword = sender_keyword
        func._dbus_path_keyword = path_keyword
        func._dbus_rel_path_keyword = rel_path_keyword
        func._dbus_destination_keyword = destination_keyword
        func._dbus_message_keyword = message_keyword
        func._dbus_connection_keyword = connection_keyword
        func._dbus_args = args
        func._dbus_get_args_options = dict(byte_arrays=byte_arrays)
        if is_py2:
            func._dbus_get_args_options['utf8_strings'] = kwargs.get(
                'utf8_strings', False)
        elif 'utf8_strings' in kwargs:
            raise TypeError("unexpected keyword argument 'utf8_strings'")
        return func

    return decorator


def signal(dbus_interface, signature=None, path_keyword=None,
           rel_path_keyword=None):
    """Factory for decorators used to mark methods of a `dbus.service.Object`
    to emit signals on the D-Bus.

    Whenever the decorated method is called in Python, after the method
    body is executed, a signal with the same name as the decorated method,
    with the given D-Bus interface, will be emitted from this object.

    :Parameters:
        `dbus_interface` : str
            The D-Bus interface whose signal is emitted
        `signature` : str
            The signature of the signal in the usual D-Bus notation

        `path_keyword` : str or None
            A keyword argument to the decorated method. If not None,
            that argument will not be emitted as an argument of
            the signal, and when the signal is emitted, it will appear
            to come from the object path given by the keyword argument.

            Note that when calling the decorated method, you must always
            pass in the object path as a keyword argument, not as a
            positional argument.

            This keyword argument cannot be used on objects where
            the class attribute ``SUPPORTS_MULTIPLE_OBJECT_PATHS`` is true.

            :Deprecated: since 0.82.0. Use `rel_path_keyword` instead.

        `rel_path_keyword` : str or None
            A keyword argument to the decorated method. If not None,
            that argument will not be emitted as an argument of
            the signal.

            When the signal is emitted, if the named keyword argument is given,
            the signal will appear to come from the object path obtained by
            appending the keyword argument to the object's object path.
            This is useful to implement "fallback objects" (objects which
            own an entire subtree of the object-path tree).

            If the object is available at more than one object-path on the
            same or different connections, the signal will be emitted at
            an appropriate object-path on each connection - for instance,
            if the object is exported at /abc on connection 1 and at
            /def and /x/y/z on connection 2, and the keyword argument is
            /foo, then signals will be emitted from /abc/foo and /def/foo
            on connection 1, and /x/y/z/foo on connection 2.

            :Since: 0.82.0
    """
    validate_interface_name(dbus_interface)

    if path_keyword is not None:
        from warnings import warn
        warn(DeprecationWarning('dbus.service.signal::path_keyword has been '
                                'deprecated since dbus-python 0.82.0, and '
                                'will not work on objects that support '
                                'multiple object paths'),
             DeprecationWarning, stacklevel=2)
        if rel_path_keyword is not None:
            raise TypeError('dbus.service.signal::path_keyword and '
                            'rel_path_keyword cannot both be used')

    def decorator(func):
        member_name = func.__name__
        validate_member_name(member_name)

        def emit_signal(self, *args, **keywords):
            abs_path = None
            if path_keyword is not None:
                if self.SUPPORTS_MULTIPLE_OBJECT_PATHS:
                    raise TypeError('path_keyword cannot be used on the '
                                    'signals of an object that supports '
                                    'multiple object paths')
                abs_path = keywords.pop(path_keyword, None)
                if (abs_path != self.__dbus_object_path__ and
                    not self.__dbus_object_path__.startswith(abs_path + '/')):
                    raise ValueError('Path %r is not below %r', abs_path,
                                     self.__dbus_object_path__)

            rel_path = None
            if rel_path_keyword is not None:
                rel_path = keywords.pop(rel_path_keyword, None)

            func(self, *args, **keywords)

            for location in self.locations:
                if abs_path is None:
                    # non-deprecated case
                    if rel_path is None or rel_path in ('/', ''):
                        object_path = location[1]
                    else:
                        # will be validated by SignalMessage ctor in a moment
                        object_path = location[1] + rel_path
                else:
                    object_path = abs_path

                message = SignalMessage(object_path,
                                                       dbus_interface,
                                                       member_name)
                message.append(signature=signature, *args)

                location[0].send_message(message)
        # end emit_signal

        args = inspect.getargspec(func)[0]
        args.pop(0)

        for keyword in rel_path_keyword, path_keyword:
            if keyword is not None:
                try:
                    args.remove(keyword)
                except ValueError:
                    raise ValueError('function has no argument "%s"' % keyword)

        if signature:
            sig = tuple(Signature(signature))

            if len(sig) > len(args):
                raise ValueError('signal signature is longer than the number of arguments provided')
            elif len(sig) < len(args):
                raise ValueError('signal signature is shorter than the number of arguments provided')

        emit_signal.__name__ = func.__name__
        emit_signal.__doc__ = func.__doc__
        emit_signal._dbus_is_signal = True
        emit_signal._dbus_interface = dbus_interface
        emit_signal._dbus_signature = signature
        emit_signal._dbus_args = args
        return emit_signal

    return decorator
