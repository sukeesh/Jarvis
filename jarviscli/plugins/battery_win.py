import os
import subprocess

import psutil
from jarviscli import entrypoint


@entrypoint
def battery_WIN32(jarvis, s):
    """
    Provides basic info about battery for win32
    """
    # https://stackoverflow.com/a/41988506/6771356

    def secs2hours(secs):
        mm, ss = divmod(secs, 60)
        hh, mm = divmod(mm, 60)
        return "%d:%02d:%02d" % (hh, mm, ss)

    batt = psutil.sensors_battery()
    if batt.power_plugged:
        jarvis.say("Battery is charging: %s%%" % batt.percent)
    else:
        jarvis.say("charge = %s%%, time left = %s" %
                   (batt.percent, secs2hours(batt.secsleft)))
