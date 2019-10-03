import subprocess
from plugin import plugin, require, LINUX, WINDOWS

VALID_OPTIONS = ['status', 'vendor', 'energy', 'technology', 'remaining']


@require(platform=WINDOWS)
@plugin('battery')
def battery_WIN32(jarvis, s):
    """
    Provides basic info about battery fo win32
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
        jarvis.say("charge = %s%%, time left = %s" % (batt.percent, secs2hours(batt.secsleft)))


@require(platform=LINUX, native='upower')
@plugin('battery')
def battery_LINUX(jarvis, s):
    """
    Provides battery status like battery percentage
    and if the battery is charging or not
    """

    # Get the battery info
    battery_info = get_specific_info(s.lower())

    # Display the battery status
    jarvis.say(battery_info)


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
        # Show the list of valid options
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

    # Convert the output from bytes to string
    output = output.decode("utf-8")

    return output
