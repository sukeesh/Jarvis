from plugin import LINUX, UNIX, MACOS, WINDOWS, plugin, require
from platform import system as sys
from colorama import Fore
import subprocess
import re
# import winreg


@require(platform=LINUX)
@plugin("mac")
class MacManagerLinux():
    """
    Jarvis plugin For viewing and changing any device MAC address connected to your computer

    """

    def __call__(self, jarvis, s):
        devices = self.request_devices(jarvis)
        jarvis.say("You have " + str(len(devices)) + " internet device/s")
        choice = self.show_options(jarvis, devices)
        device_choice = list(devices[choice - 1].keys())[0]
        mac_choice = self.get_new_mac("Please choose a new MAC address: ", jarvis)
        jarvis.say('Setting device ' + str(device_choice) + ' to MAC address: ' + str(mac_choice))    
        new_mac = self.change_mac(device_choice, mac_choice, jarvis)
        devices = self.request_devices(jarvis)
        mac = list(devices[choice - 1].values())
        name = list(devices[choice - 1].keys())
        jarvis.say("Your new MAC address is: " + str(name[0]) + ' - ' + str(mac[0]))

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
                        "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            except ValueError:
                jarvis.say(
                    "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            jarvis.say("")

    def get_new_mac(self, input_value, jarvis):
        while True:
            try:
                input_value = jarvis.input(input_value, Fore.GREEN)
                regex = re.compile(r'([0-9a-f]{2}(?::[0-9a-f]{2}){5})')
                if len(re.findall(regex, str(input_value))) == 1:
                    return input_value
                else:
                    jarvis.say("Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            except ValueError:
                jarvis.say("Invalid input! Enter a number from the choices provided.", Fore.YELLOW)

    def request_devices(self, jarvis):
        out = subprocess.Popen(["ifconfig"], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (res ,stderr )= out.communicate()
        res = str(res)
        arr = res.split("\n\n")
        arr.remove('')
        devices = []
        for x in arr:
            device_name = x.split(':')
            if device_name[0] == 'lo':
                pass
            else:
                regex = re.compile(r'([0-9a-f]{2}(?::[0-9a-f]{2}){5})')
                mac = re.findall(regex, x)
                if len(mac) == 1:
                    devices.append({device_name[0]: mac[0]})
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
        choice = self.get_choice("Please select a device or Exit: ", count, count, jarvis)
        if choice == -1:
            return
        else:
            return choice

    def change_mac(self, device, mac, jarvis):
        down = subprocess.Popen([f"sudo ifconfig {device} down"], shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        down.communicate(jarvis.input("Password for Sudo: "))
        change = subprocess.Popen([f"sudo ifconfig {device} hw ether {mac}"], shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        up = subprocess.Popen([f"sudo ifconfig {device} up"], shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        restart = subprocess.Popen(["sudo service network-manager restart"], shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        new_out = subprocess.Popen(["ifconfig"], shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (new_res ,stderr ) = new_out.communicate()
        return new_res



@require(platform=WINDOWS)
@plugin("mac")
class MacManagerWindows():
    """
    Jarvis plugin For viewing and changing any device MAC address connected to your computer

    """
    WIN_REGISTRY_PATH = "SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"

    def __call__(self, jarvis, s):
        devices = self.get_ipconfig_all()

    def restart_adapter(self, device):
        """
        Disables and then re-enables device interface
        """
        if platform.release() == 'XP':
            description, adapter_name, address, current_address = find_interface(device)
            cmd = "devcon hwids =net"
            try:
                result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            except FileNotFoundError:
                raise
            query = '('+description+'\r\n\s*.*:\r\n\s*)PCI\\\\(([A-Z]|[0-9]|_|&)*)'
            query = query.encode('ascii')
            match = re.search(query,result)
            cmd = 'devcon restart "PCI\\' + str(match.group(2).decode('ascii'))+ '"'
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            
        else:
            cmd = "netsh interface set interface \"" + device + "\" disable"
            subprocess.check_output(cmd)
            cmd = "netsh interface set interface \"" + device + "\" enable"
            subprocess.check_output(cmd)

    def get_ipconfig_all(self):
        result = subprocess.check_output(["ipconfig", "/all"], stderr=subprocess.STDOUT)
        return result.decode('ascii')

    def get_interface_mac(self, device):
        output = self.get_ipconfig_all()

        device = device.lower().strip()

        # search for specific adapter gobble through mac address
        m = re.search("adapter "+device+":[\\n\\r]+(.*?)\\s*Physical Address[^\\d]+(\\s\\S+)", output, re.I | re.DOTALL)
        if not hasattr(m, "group") or m.group(0) == None:
            return None

        adapt_mac = m.group(0)

        # extract physical address then mac
        m = re.search("Physical Address[^\\d]+(\\s\\S+)", adapt_mac)
        phy_addr = m.group(0)
        m = re.search("(?<=:\\s)(.*)", phy_addr)
        if not hasattr(m, "group") or m.group(0) == None:
            return None

        mac = m.group(0)
        return mac

    def find_interfaces(self, targets=None):
        """
        Returns the list of interfaces found on this machine as reported
        by the `ipconfig` command.
        """
        targets = [t.lower() for t in targets] if targets else []
        # Parse the output of `ipconfig /all` which gives
        # us 3 fields used:
        # - the adapter description
        # - the adapter name/device associated with this, if any,
        # - the MAC address, if any

        output = self.get_ipconfig_all()

        # search for specific adapter gobble through mac address
        details = re.findall("adapter (.*?):[\\n\\r]+(.*?)\\s*Physical Address[^\\d]+(\\s\\S+)", output, re.DOTALL)

        # extract out ipconfig results from STDOUT
        for i in range(0, len(details)):
            dns = None
            description = None
            address = None
            adapter_name = details[i][0].strip()

            # extract DNS suffix
            m = re.search("(?<=:\\s)(.*)", details[i][1])
            if hasattr(m, "group") and m.group(0) != None:
                dns = m.group(0).strip()

            # extract description then strip out value
            m = re.search("Description[^\\d]+(\\s\\S+)+", details[i][1])
            if hasattr(m, "group") and m.group(0) != None:
                descript_line = m.group(0)
                m = re.search("(?<=:\\s)(.*)", descript_line)
                if hasattr(m, "group") and m.group(0) != None:
                    description = m.group(0).strip()

            address = details[i][2].strip()

            current_address = self.get_interface_mac(adapter_name)

            if not targets:
                # Not trying to match anything in particular,
                # return everything.
                yield description, adapter_name, address, current_address
                continue

            for target in targets:
                if target in (adapter_name.lower(), adapter_name.lower()):
                    yield description, adapter_name, address, current_address
                    break

    def find_interface(self, target):
        """
        Returns tuple of the first interface which matches `target`.
            adapter description, adapter name, mac address of target, current mac addr
        """
        try:
            return next(self.find_interfaces(targets=[target]))
        except StopIteration:
            pass

    def set_interface_mac(self, device, mac, port=None):
        description, adapter_name, address, current_address = self.find_interface(device)

        # Locate adapter's registry and update network address (mac)
        reg_hdl = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(reg_hdl, self.WIN_REGISTRY_PATH)
        info = winreg.QueryInfoKey(key)

        # Find adapter key based on sub keys
        adapter_key = None
        adapter_path = None

        
        for x in range(info[0]):
            subkey = winreg.EnumKey(key, x)
            path = self.WIN_REGISTRY_PATH + "\\" + subkey

            if subkey == 'Properties':
                break

            # Check for adapter match for appropriate interface
            new_key = winreg.OpenKey(reg_hdl, path)
            try:
                adapterDesc = winreg.QueryValueEx(new_key, "DriverDesc")
                if adapterDesc[0] == description:
                    adapter_path = path
                    break
                else:
                    winreg.CloseKey(new_key)
            except (WindowsError) as err:
                if err.errno == 2:  # register value not found, ok to ignore
                    pass
                else:
                    raise err

        if adapter_path is None:
            winreg.CloseKey(key)
            winreg.CloseKey(reg_hdl)
            return

        # Registry path found update mac addr
        adapter_key = winreg.OpenKey(reg_hdl, adapter_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(adapter_key, "NetworkAddress", 0, winreg.REG_SZ, normalise(mac))
        winreg.CloseKey(adapter_key)
        winreg.CloseKey(key)
        winreg.CloseKey(reg_hdl)

        # Adapter must be restarted in order for change to take affect
        self.restart_adapter(adapter_name)