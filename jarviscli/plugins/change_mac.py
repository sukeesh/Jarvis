import re
import subprocess
from platform import system as sys

from colorama import Fore

from plugin import LINUX, plugin, require


@require(platform=LINUX)
@plugin("mac")
class MacManagerLinux():
    """
    Jarvis plugin for viewing and changing any devices MAC
    address connected to your computer

    """

    def __call__(self, jarvis, s):
        devices = self.request_devices(jarvis)
        jarvis.say("You have " + str(len(devices)) + " internet device/s")
        choice = self.show_options(jarvis, devices)
        if choice == "exit":
            return
        device_choice = list(devices[choice - 1].keys())[0]
        mac_choice = self.get_new_mac(
            "Please choose a new MAC address: ", jarvis)
        jarvis.say('Setting device ' + str(device_choice) +
                   ' to MAC address: ' + str(mac_choice))
        new_mac = self.change_mac(device_choice, mac_choice, jarvis)
        devices = self.request_devices(jarvis)
        mac = list(devices[choice - 1].values())
        name = list(devices[choice - 1].keys())
        jarvis.say("Your new MAC address is: " +
                   str(name[0]) + ' - ' + str(mac[0]))

    def get_choice(self, input_text, max_valid_value, terminator, jarvis):
        while True:
            try:
                inserted_value = int(jarvis.input(input_text, Fore.GREEN))
                if inserted_value == terminator:
                    return -1
                elif inserted_value <= max_valid_value:
                    return inserted_value
                else:
                    jarvis.say(
                        "Invalid input! Enter a number from the"
                        "choices provided.", Fore.YELLOW)
            except ValueError:
                jarvis.say(
                    "Invalid input! Enter a number from the choices provided.",
                    Fore.YELLOW)
            jarvis.say("")

    def get_new_mac(self, input_value, jarvis):
        while True:
            try:
                input_value = jarvis.input(input_value, Fore.GREEN)
                regex = re.compile(r'([0-9a-f]{2}(?::[0-9a-f]{2}){5})')
                if len(re.findall(regex, str(input_value))) == 1:
                    return input_value
                else:
                    jarvis.say("Invalid input! Enter a number"
                               "from the choices provided.", Fore.YELLOW)
            except ValueError:
                jarvis.say("Invalid input! Enter a number"
                           "from the choices provided.", Fore.YELLOW)

    def request_devices(self, jarvis):
        out = subprocess.Popen(["ip link"], universal_newlines=True,
                               shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                               )
        (res, stderr) = out.communicate()
        res = str(res)
        arr = res.split('\n')
        arr.remove('')
        span = 2
        arr1 = ["\n".join(arr[i:i + span]) for i in range(0, len(arr), span)]
        devices = []
        for x in arr1:
            device_name = x.split(':')
            if device_name[1].strip() == 'lo':
                pass
            else:
                regex = re.compile(r'([0-9a-f]{2}(?::[0-9a-f]{2}){5})')
                mac = re.findall(regex, x)
                if len(mac) >= 1:
                    devices.append({device_name[1].strip(): mac[0]})
                else:
                    pass
        return devices

    def show_options(self, jarvis, arr):
        count = 1
        for x in range(len(arr)):
            mac = list(arr[x].values())
            name = list(arr[x].keys())
            jarvis.say(str(count) + ": " + str(name[0]) + ' - ' + str(mac[0]))
            count = count + 1
        jarvis.say(str(count) + ": Exit")
        choice = self.get_choice("Please select a device or Exit: ",
                                 count, count, jarvis)
        if choice == -1:
            return "exit"
        else:
            return choice

    def change_mac(self, device, mac, jarvis):
        down = subprocess.Popen([f"sudo ip link set {device} down"],
                                shell=True, universal_newlines=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        down.communicate()
        change = subprocess.Popen([f"sudo ip link set {device} address {mac}"],
                                  shell=True, universal_newlines=True,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        up = subprocess.Popen([f"sudo ip link set {device} up"],
                              shell=True, universal_newlines=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
        restart = subprocess.Popen(["sudo service network-manager restart"],
                                   shell=True, universal_newlines=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        new_out = subprocess.Popen(["ip link"], shell=True,
                                   universal_newlines=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        (new_res, stderr) = new_out.communicate()
        return new_res
