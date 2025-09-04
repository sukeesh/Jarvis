from plugin import plugin
from colorama import Fore
import re


def format_time(seconds):
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minutes {int(seconds % 60)} seconds"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{int(hours)} hours {int(minutes)} minutes"
    elif seconds < 604800:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{int(days)} days {int(hours)} hours"
    else:
        weeks = seconds // 604800
        days = (seconds % 604800) // 86400
        return f"{int(weeks)} weeks {int(days)} days"


def convert_to_megabytes(size, unit):
    if unit == "KB":
        size /= 1024
    elif unit == "GB":
        size *= 1024
    elif unit == "TB":
        size *= 1024 * 1024
    return size


@plugin("download_calc")
def download_calc(jarvis, s):
    """
    Calculates the estimated time for a download to complete given the data size and download speed.
    The data can be given in MegaBytes (MB) or GigaBytes (GB) or TerraBytes (TB). For simplicity's sake, bits will
    not be considered, as most file sizes are now in bytes, and many people confuse Megabits (Mb) and MegaBytes (MB).
    The estimated download time will be simplified to the biggest denominator, but will still use the smaller
    denominations. I.E, 82 seconds will be simplified to 1 minute and 12 seconds, and 190 minutes and 20 seconds will
    be simplified to 3 hours, 10 minutes and 20 seconds.
    """

    s = jarvis.input("Please enter the download size, with the denomination MB, GB or TB: ", Fore.YELLOW)

    # ensure input is correct format, i.e. digits followed by a denominator
    valid = re.match(r'([\d.]+)\s*(MB|GB|TB|mb|gb|tb)', s)
    while not valid:
        jarvis.say("Invalid format, please try again, or cancel with c: ", Fore.RED)
        s = jarvis.input("")
        if s == "c":
            return
        valid = re.match(r'([\d.]+)\s*(MB|GB|TB|mb|gb|tb)', s)

    # extract data from data size input
    try:
        data_size = float(valid.group(1))
    except ValueError:
        jarvis.say("The provided download size is invalid.", Fore.RED)
        return
    data_denom = valid.group(2).upper()

    s = jarvis.input("Please enter your download speed (per second), with the denomination KB, MB or GB: ", Fore.YELLOW)

    # ensure input is correct format, i.e. digits followed by a denominator
    valid = re.match(r'([\d.]+)\s*(KB|MB|GB|TB|kb|mb|gb|tb)', s)
    while not valid:
        jarvis.say("Invalid format, please try again, or cancel with c: ", Fore.RED)
        s = jarvis.input("")
        if s == "c":
            return
        valid = re.match(r'([\d.]+)\s*(KB|MB|GB|TB|kb|mb|gb|tb)', s)

    # extract data from download speed input
    try:
        download_speed = float(valid.group(1))
    except ValueError:
        jarvis.say("The provided download speed is invalid.", Fore.RED)
        return
    download_denom = valid.group(2).upper()

    # normalise values to MegaBytes and MegaBytes per second
    data_size = convert_to_megabytes(data_size, data_denom)
    download_speed = convert_to_megabytes(download_speed, download_denom)

    # calculate and simplify estimated download time
    estimated = data_size / download_speed
    estimated = format_time(estimated)

    jarvis.say(f"Download will complete in approximately {estimated}.", Fore.GREEN)
