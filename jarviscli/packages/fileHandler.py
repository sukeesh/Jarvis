# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime as dt
from colorama import Fore

timeFormat = "%Y-%m-%d %H:%M:%S"


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, dt):
        serial = obj.strftime(timeFormat)
        return serial
    raise TypeError("Type not serializable")


def read_file(name, default=None):
    if os.path.exists(name):
        try:
            with open(name, "r+") as f:
                return json.load(f)
        except ValueError:
            print(
                Fore.RED
                + "Storage file not in right format. Backup stored as {0}.bak".format(name)
                + Fore.RESET)
            os.rename(name, name + ".bak")
    return default


def write_file(name, obj):
    with open(name, "w+") as f:
        json.dump(obj, f, default=json_serial)


def str2date(string):
    return dt.strptime(string, timeFormat)
