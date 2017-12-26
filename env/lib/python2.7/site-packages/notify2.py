"""This is a pure-python replacement for notify-python, using python-dbus
to communicate with the notifications server directly. It's compatible with
Python 2 and 3, and its callbacks can work with Gtk 3 or Qt 4 applications.

To use it, first call ``notify2.init('app name')``, then create and show notifications::

    n = notify2.Notification("Summary",
                             "Some body text",
                             "notification-message-im"   # Icon name
                            )
    n.show()

API docs are `available on ReadTheDocs <https://notify2.readthedocs.org/en/latest/>`_,
or you can refer to docstrings.

Based on the notifications spec at:
http://developer.gnome.org/notification-spec/

Porting applications from pynotify
----------------------------------

There are a few differences from pynotify you should be aware of:

- If you need callbacks from notifications, notify2 must know about your event
  loop. The simplest way is to pass 'glib' or 'qt' as the ``mainloop`` parameter
  to ``init``.
- The methods ``attach_to_widget`` and ``attach_to_status_icon`` are not
  implemented. You can calculate the location you want the notification to
  appear and call ``Notification``.
- ``set_property`` and ``get_property`` are not implemented. The summary, body
  and icon are accessible as attributes of a ``Notification`` instance.
- Various methods that pynotify Notification instances got from gobject do not
  exist, or only implement part of the functionality.

Several pynotify functions, especially getters and setters, are only supported
for compatibility. You are encouraged to use more direct, Pythonic alternatives.
"""

import dbus

__version__ = '0.3.1'

# Constants
EXPIRES_DEFAULT = -1
EXPIRES_NEVER = 0

URGENCY_LOW = 0
URGENCY_NORMAL = 1
URGENCY_CRITICAL = 2
urgency_levels = [URGENCY_LOW, URGENCY_NORMAL, URGENCY_CRITICAL]

# Initialise the module (following pynotify's API) -----------------------------

initted = False
appname = ""
_have_mainloop = False

class UninittedError(RuntimeError):
    """Error raised if you try to communicate with the server before calling
    :func:`init`.
    """
    pass

class UninittedDbusObj(object):
    def __getattr__(self, name):
        raise UninittedError("You must call notify2.init() before using the "
                             "notification features.")

dbus_iface = UninittedDbusObj()

def init(app_name, mainloop=None):
    """Initialise the D-Bus connection. Must be called before you send any
    notifications, or retrieve server info or capabilities.
    
    To get callbacks from notifications, DBus must be integrated with a mainloop.
    There are three ways to achieve this:
    
    - Set a default mainloop (dbus.set_default_main_loop) before calling init()
    - Pass the mainloop parameter as a string 'glib' or 'qt' to integrate with
      those mainloops. (N.B. passing 'qt' currently makes that the default dbus
      mainloop, because that's the only way it seems to work.)
    - Pass the mainloop parameter a DBus compatible mainloop instance, such as
      dbus.mainloop.glib.DBusGMainLoop().
    
    If you only want to display notifications, without receiving information
    back from them, you can safely omit mainloop.
    """
    global appname, initted, dbus_iface, _have_mainloop
    
    if mainloop == 'glib':
        from dbus.mainloop.glib import DBusGMainLoop
        mainloop = DBusGMainLoop()
    elif mainloop == 'qt':
        from dbus.mainloop.qt import DBusQtMainLoop
        # For some reason, this only works if we make it the default mainloop
        # for dbus. That might make life tricky for anyone trying to juggle two
        # event loops, but I can't see any way round it.
        mainloop = DBusQtMainLoop(set_as_default=True)
    
    bus = dbus.SessionBus(mainloop=mainloop)

    dbus_obj = bus.get_object('org.freedesktop.Notifications',
                              '/org/freedesktop/Notifications')
    dbus_iface = dbus.Interface(dbus_obj,
                                dbus_interface='org.freedesktop.Notifications')
    appname = app_name
    initted = True
    
    if mainloop or dbus.get_default_main_loop():
        _have_mainloop = True
        dbus_iface.connect_to_signal('ActionInvoked', _action_callback)
        dbus_iface.connect_to_signal('NotificationClosed', _closed_callback)
        
    return True

def is_initted():
    """Has init() been called? Only exists for compatibility with pynotify.
    """
    return initted

def get_app_name():
    """Return appname. Only exists for compatibility with pynotify.
    """
    return appname

def uninit():
    """Undo what init() does."""
    global initted, dbus_iface, _have_mainloop
    initted = False
    _have_mainloop = False
    dbus_iface = UninittedDbusObj()

# Retrieve basic server information --------------------------------------------

def get_server_caps():
    """Get a list of server capabilities.
    
    These are short strings, listed `in the spec <http://people.gnome.org/~mccann/docs/notification-spec/notification-spec-latest.html#commands>`_.
    Vendors may also list extra capabilities with an 'x-' prefix, e.g. 'x-canonical-append'.
    """
    return [str(x) for x in dbus_iface.GetCapabilities()]

def get_server_info():
    """Get basic information about the server.
    """
    res = dbus_iface.GetServerInformation()
    return {'name': str(res[0]),
             'vendor': str(res[1]),
             'version': str(res[2]),
             'spec-version': str(res[3]),
            }

# Action callbacks -------------------------------------------------------------

notifications_registry = {}

def _action_callback(nid, action):
    nid, action = int(nid), str(action)
    try:
        n = notifications_registry[nid]
    except KeyError:
        #this message was created through some other program.
        return
    n._action_callback(action)

def _closed_callback(nid, reason):
    nid, reason = int(nid), int(reason)
    try:
        n = notifications_registry[nid]
    except KeyError:
        #this message was created through some other program.
        return
    n._closed_callback(n)
    del notifications_registry[nid]

def no_op(*args):
    """No-op function for callbacks.
    """
    pass

# Controlling notifications ----------------------------------------------------

ActionsDictClass = dict  # fallback for old version of Python
try:
    from collections import OrderedDict
    ActionsDictClass = OrderedDict
except ImportError:
    pass


class Notification(object):
    """A notification object.
    
    summary : str
      The title text
    message : str
      The body text, if the server has the 'body' capability.
    icon : str
      Path to an icon image, or the name of a stock icon. Stock icons available
      in Ubuntu are `listed here <https://wiki.ubuntu.com/NotificationDevelopmentGuidelines#How_do_I_get_these_slick_icons>`_.
      You can also set an icon from data in your application - see
      :meth:`set_icon_from_pixbuf`.
    """
    id = 0
    timeout = -1    # -1 = server default settings
    _closed_callback = no_op
    
    def __init__(self, summary, message='', icon=''):
        self.summary = summary
        self.message = message
        self.icon = icon
        self.hints = {}
        self.actions = ActionsDictClass()
        self.data = {}     # Any data the user wants to attach
    
    def show(self):
        """Ask the server to show the notification.
        
        Call this after you have finished setting any parameters of the
        notification that you want.
        """
        nid = dbus_iface.Notify(appname,       # app_name       (spec names)
                              self.id,       # replaces_id
                              self.icon,     # app_icon
                              self.summary,  # summary
                              self.message,  # body
                              self._make_actions_array(),  # actions
                              self.hints,    # hints
                              self.timeout,  # expire_timeout
                            )
        
        self.id = int(nid)
        
        if _have_mainloop:
            notifications_registry[self.id] = self
        return True
    
    def update(self, summary, message="", icon=None):
        """Replace the summary and body of the notification, and optionally its
        icon. You should call :meth:`show` again after this to display the
        updated notification.
        """
        self.summary = summary
        self.message = message
        if icon is not None:
            self.icon = icon
    
    def close(self):
        """Ask the server to close this notification."""
        if self.id != 0:
            dbus_iface.CloseNotification(self.id)
    
    def set_hint(self, key, value):
        """n.set_hint(key, value) <--> n.hints[key] = value
        
        See `hints in the spec <http://people.gnome.org/~mccann/docs/notification-spec/notification-spec-latest.html#hints>`_.
        
        Only exists for compatibility with pynotify.
        """
        self.hints[key] = value
    
    set_hint_string = set_hint_int32 = set_hint_double = set_hint
    
    def set_hint_byte(self, key, value):
        """Set a hint with a dbus byte value. The input value can be an
        integer or a bytes string of length 1.
        """
        self.hints[key] = dbus.Byte(value)
    
    def set_urgency(self, level):
        """Set the urgency level to one of URGENCY_LOW, URGENCY_NORMAL or
        URGENCY_CRITICAL.
        """
        if level not in urgency_levels:
            raise ValueError("Unknown urgency level specified", level)
        self.set_hint_byte("urgency", level)
    
    def set_category(self, category):
        """Set the 'category' hint for this notification.
        
        See `categories in the spec <http://people.gnome.org/~mccann/docs/notification-spec/notification-spec-latest.html#categories>`_.
        """
        self.hints['category'] = category
    
    def set_timeout(self, timeout):
        """Set the display duration in milliseconds, or one of the special
        values EXPIRES_DEFAULT or EXPIRES_NEVER. This is a request, which the
        server might ignore.
        
        Only exists for compatibility with pynotify; you can simply set::
        
          n.timeout = 5000
        """
        if not isinstance(timeout, int):
            raise TypeError("timeout value was not int", timeout)
        self.timeout = timeout
    
    def get_timeout(self):
        """Return the timeout value for this notification.
        
        Only exists for compatibility with pynotify; you can inspect the
        timeout attribute directly.
        """
        return self.timeout
    
    def add_action(self, action, label, callback, user_data=None):
        """Add an action to the notification.
        
        Check for the 'actions' server capability before using this.
        
        action : str
          A brief key.
        label : str
          The text displayed on the action button
        callback : callable
          A function taking at 2-3 parameters: the Notification object, the
          action key and (if specified) the user_data.
        user_data :
          An extra argument to pass to the callback.
        """
        self.actions[action] = (label, callback, user_data)
    
    def _make_actions_array(self):
        """Make the actions array to send over DBus.
        """
        arr = []
        for action, (label, callback, user_data) in self.actions.items():
            arr.append(action)
            arr.append(label)
        return arr
    
    def _action_callback(self, action):
        """Called when the user selects an action on the notification, to
        dispatch it to the relevant user-specified callback.
        """
        try:
            label, callback, user_data = self.actions[action]
        except KeyError:
            return
        
        if user_data is None:
            callback(self, action)
        else:
            callback(self, action, user_data)
    
    def connect(self, event, callback):
        """Set the callback for the notification closing; the only valid value
        for event is 'closed' (the parameter is kept for compatibility with pynotify).
        
        The callback will be called with the :class:`Notification` instance.
        """
        if event != 'closed':
            raise ValueError("'closed' is the only valid value for event", event)
        self._closed_callback = callback
    
    def set_data(self, key, value):
        """n.set_data(key, value) <--> n.data[key] = value
        
        Only exists for compatibility with pynotify.
        """
        self.data[key] = value
    
    def get_data(self, key):
        """n.get_data(key) <--> n.data[key]
        
        Only exists for compatibility with pynotify.
        """
        return self.data[key]

    def set_icon_from_pixbuf(self, icon):
        """Set a custom icon from a GdkPixbuf.
        """
        struct = (
            icon.get_width(),
            icon.get_height(),
            icon.get_rowstride(),
            icon.get_has_alpha(),
            icon.get_bits_per_sample(),
            icon.get_n_channels(),
            dbus.ByteArray(icon.get_pixels())
            )
        self.hints['icon_data'] = struct
    
    def set_location(self, x, y):
        """Set the notification location as (x, y), if the server supports it.
        """
        if (not isinstance(x, int)) or (not isinstance(y, int)):
            raise TypeError("x and y must both be ints", (x,y))
        self.hints['x'] = x
        self.hints['y'] = y
        
