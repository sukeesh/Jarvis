import os
import subprocess

from plugin import LINUX, WINDOWS, plugin, require

VALID_OPTIONS = ['status', 'vendor', 'energy', 'technology', 'remaining']


@require(platform=WINDOWS)
@plugin('battery')
def battery_WIN32(jarvis, s):
    """
    Provides basic info about battery for win32
    """
    # https://stackoverflow.com/a/41988506/6771356
    import psutil

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


@require(platform=LINUX, native='upower')
@plugin('battery')
def battery_LINUX(jarvis, s):
    """
    Provides battery status eg: percentage
    """

    # Get the battery info using upower
    jarvis.say(get_specific_info(s.lower()))


def get_specific_info(info_required):
    """
    Gets specific information about the battery
    as per the argument 'info_required'

    Example:
        get_specific_info("vendor") - Returns the vendor of the battery
        get_specific_info("status") - Returns the status of the battery
    """

    # List containing the command to run to find the specific
    # info in a group of battery related information
    grep_command = ["grep", "-E"]

    grep_text = {
        'status': "state|to full|percentage",
        'vendor': "vendor",
        'energy': "energy",
        'technology': "technology",
        'remaining': "time to empty",
    }.get(info_required, "default")

    # If the user has entered a valid option
    if grep_text != "default":
        grep_command.append(grep_text)
    else:
        # User has entered something invalid
        return "Invalid option given. Here's a list of options:\n" + \
               ', '.join(VALID_OPTIONS)

    # Run command to get full information about the battery
    battery_info_command = subprocess.Popen([
        "upower",
        "-i",
        "/org/freedesktop/UPower/devices/battery_BAT0"
    ],
        stdout=subprocess.PIPE
    )

    # From the above output, only get the specific info required
    specific_info_command = subprocess.Popen(grep_command,
                                             stdin=battery_info_command.stdout,
                                             stdout=subprocess.PIPE
                                             )

    battery_info_command.stdout.close()

    # Get the output after piping both the commands
    output = specific_info_command.communicate()[0]

    output = output.decode("utf-8")

    return output


@require(platform=LINUX, native='!upower')
@plugin('battery')
def battery_linux_fallback(jarvis, s):
    """
    Provides battery status like battery percentage
    and if the battery is charging or not
    """

    # Get the battery info
    # https://askubuntu.com/a/309146
    battery_dir = False
    for bat_num in range(10):
        battery_dir_check = "/sys/class/power_supply/BAT{}/".format(str(bat_num))
        if os.path.exists(battery_dir_check):
            battery_dir = battery_dir_check
            break

    if battery_dir is False:
        jarvis.say("No Battery found!")
        return

    def get_battery_info(info):
        return subprocess.check_output(["cat", battery_dir + info]).decode("utf-8")[:-1]

    battery_text = ["Status: " + get_battery_info("status"), "Charge: " + get_battery_info("capacity") + "%"]

    battery_info = '\n'.join(battery_text)

    jarvis.say(battery_info)
