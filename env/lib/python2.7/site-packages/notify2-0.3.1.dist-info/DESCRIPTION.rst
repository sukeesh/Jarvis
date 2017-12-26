This is a pure-python replacement for notify-python, using python-dbus
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


