<<<<<<< HEAD
from plugin import LINUX, plugin, require
from platform import system as sys
from colorama import Fore
import subprocess
import re
=======
import re
import subprocess
from platform import system as sys

from colorama import Fore

from plugin import LINUX, plugin, require
>>>>>>> master


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
<<<<<<< HEAD
                                "Please choose a new MAC address: ", jarvis)
=======
            "Please choose a new MAC address: ", jarvis)
>>>>>>> master
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
<<<<<<< HEAD
        out = subprocess.Popen(["ifconfig"], universal_newlines=True,
=======
        out = subprocess.Popen(["ip link"], universal_newlines=True,
                               shell=True,
>>>>>>> master
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                               )
        (res, stderr) = out.communicate()
        res = str(res)
<<<<<<< HEAD
        arr = res.split("\n\n")
        arr.remove('')
        devices = []
        for x in arr:
            device_name = x.split(':')
            if device_name[0] == 'lo':
=======
        arr = res.split('\n')
        arr.remove('')
        span = 2
        arr1 = ["\n".join(arr[i:i + span]) for i in range(0, len(arr), span)]
        devices = []
        for x in arr1:
            device_name = x.split(':')
            if device_name[1].strip() == 'lo':
>>>>>>> master
                pass
            else:
                regex = re.compile(r'([0-9a-f]{2}(?::[0-9a-f]{2}){5})')
                mac = re.findall(regex, x)
<<<<<<< HEAD
                if len(mac) == 1:
                    devices.append({device_name[0]: mac[0]})
=======
                if len(mac) >= 1:
                    devices.append({device_name[1].strip(): mac[0]})
>>>>>>> master
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
<<<<<<< HEAD
        down = subprocess.Popen([f"sudo ifconfig {device} down"],
=======
        down = subprocess.Popen([f"sudo ip link set {device} down"],
>>>>>>> master
                                shell=True, universal_newlines=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        down.communicate()
<<<<<<< HEAD
        change = subprocess.Popen([f"sudo ifconfig {device} hw ether {mac}"],
                                  shell=True, universal_newlines=True,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        up = subprocess.Popen([f"sudo ifconfig {device} up"],
=======
        change = subprocess.Popen([f"sudo ip link set {device} address {mac}"],
                                  shell=True, universal_newlines=True,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        up = subprocess.Popen([f"sudo ip link set {device} up"],
>>>>>>> master
                              shell=True, universal_newlines=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)
        restart = subprocess.Popen(["sudo service network-manager restart"],
                                   shell=True, universal_newlines=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
<<<<<<< HEAD
        new_out = subprocess.Popen(["ifconfig"], shell=True,
=======
        new_out = subprocess.Popen(["ip link"], shell=True,
>>>>>>> master
                                   universal_newlines=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        (new_res, stderr) = new_out.communicate()
        return new_res
