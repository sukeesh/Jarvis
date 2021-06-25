from plugin import LINUX, WINDOWS, plugin, require
from colorama import Fore
import subprocess


@require(platform=LINUX)
@plugin("wifi")
class WifiPasswordGetterLINUX:
    """
    A Jarvis plugin for Linux, that will find and display all the profiles of the
    wifis that you have connected to and then display the password if selected.

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
        """
        Returns the names of the connected wifis.
        """
        out = subprocess.Popen(["ls",
                                "/etc/NetworkManager/system-connections/"],
                               universal_newlines=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        (res, stderr) = out.communicate()
        data = res.split('\n')
        return data

    def show_options(self, jarvis, arr):
        """
        Displays the names of the connected wifis and returns the number of the selected.

        Parameters
        ----------
        jarvis: JarvisAPI
            An instance of the JarvisAPI class.
        arr: list
            The list with the wifi names.
        """
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
        """
        Returns the number of the selected wifi.

        Parameters
        ----------
        input_text: str
            The text to be printed when asking for input.
        max_valid_value: int
            The max valid value for the choices.
        terminator: int
            The value to terminate the procedure.
        jarvis: JarvisAPI
            An instance of the JarvisAPI class.
        """
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
        """
        Returns the password of the selected wifi.

        Parameters
        ----------
        ssid: str
            The name of the selected wifi.
        """
        path = "/etc/NetworkManager/system-connections/"
        display = subprocess.Popen([f"sudo grep -r '^psk=' {path}{ssid}"],
                                   shell=True, universal_newlines=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        (new_res, stderr) = display.communicate()
        return new_res


@require(platform=WINDOWS)
@plugin("wifi")
class WifiPasswordGetterWINDOWS:
    """
    A Jarvis plugin for Windows, that will find and display all the profiles of the
    wifis that you have connected to and then display the password, if selected or
    display instantly the password of the requested wifi, e.g. wifi or wifi wifi_name.
    """

    def __call__(self, jarvis, s):
        if s:
            self.display_password(jarvis, s)
        else:
            profiles = self.get_wifi_profiles()
            if len(profiles) == 0:
                jarvis.say("No connected wifi found!", Fore.YELLOW)
                return
            choice = self.show_options(jarvis, profiles)
            if choice == -1:
                return
            self.display_password(jarvis, profiles[choice - 1])

    def get_wifi_profiles(self):
        """
        Returns the names of the connected wifis.
        """
        meta_data = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'profiles'])
        data = meta_data.decode('utf-8', errors="backslashreplace")
        data = data.split('\n')
        profiles = []
        for i in data:
            if "All User Profile" in i:
                i = i.split(":")
                i = i[1]
                i = i[1:-1]
                profiles.append(i)

        return profiles

    def show_options(self, jarvis, profiles):
        """
        Displays the names of the connected wifis and returns the number of the selected.

        Parameters
        ----------
        jarvis: JarvisAPI
            An instance of the JarvisAPI class.
        profiles: list
            The list with the wifi names.
        """
        count = 1
        for profile in profiles:
            jarvis.say(str(count) + ": " + profile)
            count = count + 1
        jarvis.say(str(count) + ": Exit")
        choice = self.get_choice(jarvis, "Please select a number or Exit: ",
                                 count)
        return choice

    def get_choice(self, jarvis, input_text, max_valid_value):
        """
        Returns the number of the selected wifi.

        Parameters
        ----------
        jarvis: JarvisAPI
            An instance of the JarvisAPI class.
        input_text: str
            The text to be printed when asking for input.
        max_valid_value: int
            The max valid value for the choices.
        """
        while True:
            try:
                inserted_value = int(jarvis.input(input_text, Fore.GREEN))
                if inserted_value == max_valid_value:
                    return -1
                elif max_valid_value > inserted_value >= 1:
                    return inserted_value
                else:
                    jarvis.say(
                        "Invalid input! Enter a number from the"
                        " choices provided.", Fore.YELLOW)
            except ValueError:
                jarvis.say(
                    "Invalid input! Enter a number from the choices provided.",
                    Fore.YELLOW)

    def display_password(self, jarvis, profile):
        """
        Displays the name and the password of the selected wifi.

        Parameters
        ----------
        profile: str
            The name of the selected wifi.
        jarvis: JarvisAPI
            An instance of the JarvisAPI class.
        """
        try:
            results = subprocess.check_output(
                ['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'])
            results = results.decode('utf-8', errors="backslashreplace")
            results = results.split('\n')
            results = [b.split(":")[1][1:-1]
                       for b in results if "Key Content" in b]
            try:
                jarvis.say("Wifi Name: " + profile +
                           '\nPassword: ' + results[0])

            except IndexError:
                jarvis.say("Wifi Name: " + profile +
                           '\nPassword: ' + "UNKNOWN")

        except subprocess.CalledProcessError:
            jarvis.say(
                "Unable to get the password for this wifi. Make sure you enter the correct wifi name!",
                Fore.YELLOW)
