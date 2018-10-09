from utilities.GeneralUtilities import IS_MACOS, executable_exists
from six import PY2


NOTIFY_LOW = 0
NOTIFY_NORMAL = 1
NOTIFY_CRITICAL = 2


notify = None


def notify__MAC(name, body, urgency=NOTIFY_NORMAL):
    pync.notify(str(name), str(body))


LINUX_URGENCY_CONVERTER = {0: 'low', 1: 'normal', 2: 'critical'}


def notify__LINUX(name, body, urgency=NOTIFY_NORMAL):
    urgency = LINUX_URGENCY_CONVERTER[urgency]
    system("notify-send -u {} '{}' '{}'".format(urgency, str(name), str(body)))


GUI_FALLBACK_DISPLAY_TIME = 3000


def notify__GUI_FALLBACK(name, body, urgency=NOTIFY_NORMAL):
    def notify_implementation():
        root = tk.Tk()
        root.after(GUI_FALLBACK_DISPLAY_TIME, root.destroy)
        root.withdraw()
        try:
            tkMessageBox.showinfo(str(name), str(body))
            root.destroy()
        except tk.TclError:
            # Ignore!
            # Just close and destroy tkinter window
            pass

    Thread(target=notify_implementation).start()


CLI_FALLBACK_URGENCY_CONVERTER = {0: '', 1: '!', 2: '!!!'}


def notify__CLI_FALLBACK(name, body, urgency=NOTIFY_NORMAL):
    urgency = CLI_FALLBACK_URGENCY_CONVERTER[urgency]
    print("NOTIFICATION {} ====> {} - {}".format(urgency, str(name), str(body)))


if IS_MACOS:
    import pync
    notify = notify__MAC
else:
    if executable_exists("notify-send"):
        from os import system
        notify = notify__LINUX
    else:
        try:
            if PY2:
                import TKinter as tk
                import tkMessageBox
            else:
                import tkinter as tk
                from tkinter import messagebox as tkMessageBox
            from threading import Thread
            notify = notify__GUI_FALLBACK
        except ImportError:
            notify = notify__CLI_FALLBACK
