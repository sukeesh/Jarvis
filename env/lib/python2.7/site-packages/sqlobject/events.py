from __future__ import print_function
import sys
import types
from pydispatch import dispatcher
from weakref import ref
from .compat import class_types


subclassClones = {}


def listen(receiver, soClass, signal, alsoSubclasses=True, weak=True):
    """
    Listen for the given ``signal`` on the SQLObject subclass
    ``soClass``, calling ``receiver()`` when ``send(soClass, signal,
    ...)`` is called.

    If ``alsoSubclasses`` is true, receiver will also be called when
    an event is fired on any subclass.
    """
    dispatcher.connect(receiver, signal=signal, sender=soClass, weak=weak)
    weakReceiver = ref(receiver)
    subclassClones.setdefault(soClass, []).append((weakReceiver, signal))

# We export this function:
send = dispatcher.send


class Signal(object):
    """
    Base event for all SQLObject events.

    In general the sender for these methods is the class, not the
    instance.
    """


class ClassCreateSignal(Signal):
    """
    Signal raised after class creation.  The sender is the superclass
    (in case of multiple superclasses, the first superclass).  The
    arguments are ``(new_class_name, bases, new_attrs, post_funcs,
    early_funcs)``.  ``new_attrs`` is a dictionary and may be modified
    (but ``new_class_name`` and ``bases`` are immutable).
    ``post_funcs`` is an initially-empty list that can have callbacks
    appended to it.

    Note: at the time this event is called, the new class has not yet
    been created.  The functions in ``post_funcs`` will be called
    after the class is created, with the single arguments of
    ``(new_class)``.  Also, ``early_funcs`` will be called at the
    soonest possible time after class creation (``post_funcs`` is
    called after the class's ``__classinit__``).
    """


def _makeSubclassConnections(new_class_name, bases, new_attrs,
                             post_funcs, early_funcs):
    early_funcs.insert(0, _makeSubclassConnectionsPost)


def _makeSubclassConnectionsPost(new_class):
    for cls in new_class.__bases__:
        for weakReceiver, signal in subclassClones.get(cls, []):
            receiver = weakReceiver()
            if not receiver:
                continue
            listen(receiver, new_class, signal)

dispatcher.connect(_makeSubclassConnections, signal=ClassCreateSignal)


# @@: Should there be a class reload event?  This would allow modules
# to be reloaded, possibly.  Or it could even be folded into
# ClassCreateSignal, since anything that listens to that needs to pay
# attention to reloads (or else it is probably buggy).


class RowCreateSignal(Signal):
    """
    Called before an instance is created, with the class as the
    sender.  Called with the arguments ``(instance, kwargs, post_funcs)``.
    There may be a ``connection`` argument.  ``kwargs``may be usefully
    modified.  ``post_funcs`` is a list of callbacks, intended to have
    functions appended to it, and are called with the arguments
    ``(new_instance)``.

    Note: this is not called when an instance is created from an
    existing database row.
    """


class RowCreatedSignal(Signal):
    """
    Called after an instance is created, with the class as the
    sender.  Called with the arguments ``(instance, kwargs, post_funcs)``.
    There may be a ``connection`` argument.  ``kwargs``may be usefully
    modified.  ``post_funcs`` is a list of callbacks, intended to have
    functions appended to it, and are called with the arguments
    ``(new_instance)``.

    Note: this is not called when an instance is created from an
    existing database row.
    """
# @@: An event for getting a row?  But for each row, when doing a
# select?  For .sync, .syncUpdate, .expire?


class RowDestroySignal(Signal):
    """
    Called before an instance is deleted.  Sender is the instance's
    class.  Arguments are ``(instance, post_funcs)``.

    ``post_funcs`` is a list of callbacks, intended to have
    functions appended to it, and are called with arguments ``(instance)``.
    If any of the post_funcs raises an exception, the deletion is only
    affected if this will prevent a commit.

    You cannot cancel the delete, but you can raise an exception (which will
    probably cancel the delete, but also cause an uncaught exception if not
    expected).

    Note: this is not called when an instance is destroyed through
    garbage collection.

    @@: Should this allow ``instance`` to be a primary key, so that a
    row can be deleted without first fetching it?
    """


class RowDestroyedSignal(Signal):
    """
    Called after an instance is deleted.  Sender is the instance's
    class.  Arguments are ``(instance)``.

    This is called before the post_funcs of RowDestroySignal

    Note: this is not called when an instance is destroyed through
    garbage collection.
    """


class RowUpdateSignal(Signal):
    """
    Called when an instance is updated through a call to ``.set()``
    (or a column attribute assignment).  The arguments are
    ``(instance, kwargs)``.  ``kwargs`` can be modified.  This is run
    *before* the instance is updated; if you want to look at the
    current values, simply look at ``instance``.
    """


class RowUpdatedSignal(Signal):
    """
    Called when an instance is updated through a call to ``.set()``
    (or a column attribute assignment).  The arguments are
    ``(instance, post_funcs)``. ``post_funcs`` is a list of callbacks,
    intended to have functions appended to it, and are called with the
    arguments ``(new_instance)``. This is run *after* the instance is
    updated; Works better with lazyUpdate = True.
    """


class AddColumnSignal(Signal):
    """
    Called when a column is added to a class, with arguments ``(cls,
    connection, column_name, column_definition, changeSchema,
    post_funcs)``.  This is called *after* the column has been added,
    and is called for each column after class creation.

    post_funcs are called with ``(cls, so_column_obj)``
    """


class DeleteColumnSignal(Signal):
    """
    Called when a column is removed from a class, with the arguments
    ``(cls, connection, column_name, so_column_obj, post_funcs)``.
    Like ``AddColumnSignal`` this is called after the action has been
    performed, and is called for subclassing (when a column is
    implicitly removed by setting it to ``None``).

    post_funcs are called with ``(cls, so_column_obj)``
    """

# @@: Signals for indexes and joins?  These are mostly event consumers,
# though.


class CreateTableSignal(Signal):
    """
    Called when a table is created.  If ``ifNotExists==True`` and the
    table exists, this event is not called.

    Called with ``(cls, connection, extra_sql, post_funcs)``.
    ``extra_sql`` is a list (which can be appended to) of extra SQL
    statements to be run after the table is created.  ``post_funcs``
    functions are called with ``(cls, connection)`` after the table
    has been created.  Those functions are *not* called simply when
    constructing the SQL.
    """


class DropTableSignal(Signal):
    """
    Called when a table is dropped.  If ``ifExists==True`` and the
    table doesn't exist, this event is not called.

    Called with ``(cls, connection, extra_sql, post_funcs)``.
    ``post_funcs`` functions are called with ``(cls, connection)``
    after the table has been dropped.
    """

############################################################
# Event Debugging
############################################################


def summarize_events_by_sender(sender=None, output=None, indent=0):
    """
    Prints out a summary of the senders and listeners in the system,
    for debugging purposes.
    """
    if output is None:
        output = sys.stdout
    leader = ' ' * indent
    if sender is None:
        send_list = [
            (deref(dispatcher.senders.get(sid)), listeners)
            for sid, listeners in dispatcher.connections.items()
            if deref(dispatcher.senders.get(sid))]
        for sender, listeners in sorted_items(send_list):
            real_sender = deref(sender)
            if not real_sender:
                continue
            header = 'Sender: %r' % real_sender
            print(leader + header, file=output)
            print(leader + ('=' * len(header)), file=output)
            summarize_events_by_sender(real_sender, output=output,
                                       indent=indent + 2)
    else:
        for signal, receivers in \
                sorted_items(dispatcher.connections.get(id(sender), [])):
            receivers = [deref(r) for r in receivers if deref(r)]
            header = 'Signal: %s (%i receivers)' % (sort_name(signal),
                                                    len(receivers))
            print(leader + header, file=output)
            print(leader + ('-' * len(header)), file=output)
            for receiver in sorted(receivers, key=sort_name):
                print(leader + '  ' + nice_repr(receiver), file=output)


def deref(value):
    if isinstance(value, dispatcher.WEAKREF_TYPES):
        return value()
    else:
        return value


def sorted_items(a_dict):
    if isinstance(a_dict, dict):
        a_dict = a_dict.items()
    return sorted(a_dict, key=lambda t: sort_name(t[0]))


def sort_name(value):
    if isinstance(value, type):
        return value.__name__
    elif isinstance(value, types.FunctionType):
        return value.__name__
    else:
        return str(value)

_real_dispatcher_send = dispatcher.send
_real_dispatcher_sendExact = dispatcher.sendExact
_real_dispatcher_connect = dispatcher.connect
_real_dispatcher_disconnect = dispatcher.disconnect
_debug_enabled = False


def debug_events():
    global _debug_enabled, send
    if _debug_enabled:
        return
    _debug_enabled = True
    dispatcher.send = send = _debug_send
    dispatcher.sendExact = _debug_sendExact
    dispatcher.disconnect = _debug_disconnect
    dispatcher.connect = _debug_connect


def _debug_send(signal=dispatcher.Any, sender=dispatcher.Anonymous,
                *arguments, **named):
    print("send %s from %s: %s" % (
          nice_repr(signal), nice_repr(sender),
          fmt_args(*arguments, **named)))
    return _real_dispatcher_send(signal, sender, *arguments, **named)


def _debug_sendExact(signal=dispatcher.Any, sender=dispatcher.Anonymous,
                     *arguments, **named):
    print("sendExact %s from %s: %s" % (
          nice_repr(signal), nice_repr(sender), fmt_args(*arguments, **name)))
    return _real_dispatcher_sendExact(signal, sender, *arguments, **named)


def _debug_connect(receiver, signal=dispatcher.Any, sender=dispatcher.Any,
                   weak=True):
    print("connect %s to %s signal %s" % (
          nice_repr(receiver), nice_repr(signal), nice_repr(sender)))
    return _real_dispatcher_connect(receiver, signal, sender, weak)


def _debug_disconnect(receiver, signal=dispatcher.Any, sender=dispatcher.Any,
                      weak=True):
    print("disconnecting %s from %s signal %s" % (
          nice_repr(receiver), nice_repr(signal), nice_repr(sender)))
    return _real_dispatcher_disconnect(receiver, signal, sender, weak)


def fmt_args(*arguments, **name):
    args = [repr(a) for a in arguments]
    args.extend([
        '%s=%r' % (n, v) for n, v in sorted(name.items())])
    return ', '.join(args)


def nice_repr(v):
    """
    Like repr(), but nicer for debugging here.
    """
    if isinstance(v, class_types):
        return v.__module__ + '.' + v.__name__
    elif isinstance(v, types.FunctionType):
        if '__name__' in v.__globals__:
            if getattr(sys.modules[v.__globals__['__name__']],
                       v.__name__, None) is v:
                return '%s.%s' % (v.__globals__['__name__'], v.__name__)
        return repr(v)
    elif isinstance(v, types.MethodType):
        return '%s.%s of %s' % (
            nice_repr(v.__self__.__class__), v.__func__.__name__,
            nice_repr(v.__self__))
    else:
        return repr(v)


__all__ = ['listen', 'send']
# Use copy() to avoid 'dictionary changed' issues on python 3
for name, value in globals().copy().items():
    if isinstance(value, type) and issubclass(value, Signal):
        __all__.append(name)
