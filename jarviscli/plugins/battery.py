import subprocess
from plugin import plugin, require, LINUX

VALID_OPTIONS = ['status', 'vendor', 'energy', 'technology', 'remaining']


@require(platform=LINUX, native='upower')
@plugin('battery')
def battery(jarvis, s):
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
