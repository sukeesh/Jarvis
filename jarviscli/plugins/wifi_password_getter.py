from plugin import LINUX, plugin, require
from platform import system as sys
from colorama import Fore
import subprocess


@require(platform=LINUX)
@plugin("wifi")
class wifiPasswordGetter():
    """
    A Jarvis plugin that will find and display all the profiles of the
    wifis that you have connected to and then display the password if selected

    """

    def __call__(self, jarvis, s):
        profiles = self.get_wifi_profiles()
        choice = self.show_options(jarvis, profiles)
        if choice == "exit":
            return
        password = self.display_password(profiles[choice - 1])
        strip_password = password.split("=", 1)[1]
        jarvis.say("Wifi Name: " + profiles[choice - 1] +
                   '\nPassword: ' + strip_password)

    def get_wifi_profiles(self):
        out = subprocess.Popen(["ls", "/etc/NetworkManager/system-connections/"],
                               universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (res, stderr) = out.communicate()
        data = res.split('\n')
        return data

    def show_options(self, jarvis, arr):
        count = 1
        for x in range(len(arr) - 1):
            option = arr[x]
            jarvis.say(str(count) + ": " + option)
            count = count + 1
        jarvis.say(str(count) + ": Exit")
        choice = self.get_choice("Please select a number or Exit: ",
                                 count, count, jarvis)
        if choice == -1:
            return "exit"
        else:
            return choice

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

    def display_password(self, ssid):
        path = "/etc/NetworkManager/system-connections/"
        display = subprocess.Popen([f"sudo grep -r '^psk=' {path}{ssid}"],
                                   shell=True, universal_newlines=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        (new_res, stderr) = display.communicate()
        return new_res
