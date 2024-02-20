import os
import subprocess

from jarviscli import entrypoint


@entrypoint
def battery_linux_fallback(jarvis, s):
    """
    Provides battery status like battery percentage
    and if the battery is charging or not
    """

    # Get the battery info
    # https://askubuntu.com/a/309146
    battery_dir = False
    for bat_num in range(10):
        battery_dir_check = "/sys/class/power_supply/BAT{}/".format(
            str(bat_num))
        if os.path.exists(battery_dir_check):
            battery_dir = battery_dir_check
            break

    if battery_dir is False:
        jarvis.say("No Battery found!")
        return

    def get_battery_info(info):
        return subprocess.check_output(["cat", battery_dir + info]).decode("utf-8")[:-1]

    battery_text = [
        "Status: " + get_battery_info("status"), "Charge: " + get_battery_info("capacity") + "%"]

    battery_info = '\n'.join(battery_text)

    jarvis.say(battery_info)
