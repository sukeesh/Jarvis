# -*- coding: utf-8 -*-
"""Yeelight IoT plugin.

	This plugin controls all the yeelight
	smart bulbs in the user's smart home.

	Typical usage example:

	>yeelight
	>bedroom on

	@Author: Leonidha Mara @leonidhaMara & Emmanouil Manousakis @manousakis01
	@Date: 21st June 2022
"""
from colorama import Fore
from plugin import plugin, require
from yeelight import discover_bulbs
import yeelight
from typing import List
import time


@require(network=True)
@plugin("yeelight")
class Yeelight:
    def __call__(self, jarvis, s):
        self.jarvis = jarvis
        self.main()

    def __init__(self):
        self.discovered_bulbs = {}
        self.exit_msg = "exit"

    def handle_help_command(self):
        """Display help information about available commands"""
        self.jarvis.say('[ bulb name | all][status]')
        self.jarvis.say('-The first argument is the name of the bulb or the keyword "all".')
        self.jarvis.say('-The second argument specify turning on or off the light or all the lights.')

    def find_bulb_ip(self, bulb_name):
        """Find IP address for given bulb name"""
        for ip, info in self.discovered_bulbs.items():
            if info['name'].lower() == bulb_name.lower():
                return ip
        return None

    def handle_power_command(self, bulb_name, power_state):
        """Handle power on/off commands for single bulb or all bulbs"""
        ip = self.find_bulb_ip(bulb_name) if bulb_name.lower() != 'all' else None

        if power_state == 'on':
            if ip:
                yeelight.Bulb(ip).turn_on()
                self.jarvis.say(f"Bulb {self.discovered_bulbs[ip]['name']} is on.")
            else:
                self.power_on_all()
        elif power_state == 'off':
            if ip:
                yeelight.Bulb(ip).turn_off()
                self.jarvis.say(f"Bulb {self.discovered_bulbs[ip]['name']} is off.")
            else:
                self.power_off_all()

    def main(self):
        self.jarvis.say("To exit enter word 'exit'", color=Fore.YELLOW)
        self.discover()
        
        if self.find_unknown_bulbs():
            self.name_bulbs()

        while True:
            self.display_cond()
            cmd = self.jarvis.input("Command (Use 'help' for details):", color=Fore.GREEN).split()
            
            if self.is_exit_input(cmd[0]):
                break

            if cmd[0].lower() == 'help':
                self.handle_help_command()
            else:
                self.handle_power_command(cmd[0], cmd[1].lower())

    def display_cond(self):
        """
        Display the status of all the lights that are connected to the Lan.
        """
        for v, ip in enumerate(self.discovered_bulbs):
            self.jarvis.say(
                f"Name: {self.discovered_bulbs[ip]['name']}   Status: { yeelight.Bulb(ip).get_properties()['power']}")

    def power_on_all(self):
        """
        Turn on all the lights
        """
        for ip in self.discovered_bulbs:
            yeelight.Bulb(ip).turn_on()
            name = self.discovered_bulbs[ip]['name']
            if name:
                self.jarvis.say(f"Bulb {name} is on.")
            else:
                self.jarvis.say(f"Bulb {ip} is on.")

    def power_off_all(self):
        """
        Turn off all the lights
        """
        for ip in self.discovered_bulbs:
            yeelight.Bulb(ip).turn_off()
            name = self.discovered_bulbs[ip]['name']
            if name:
                self.jarvis.say(f"Bulb {name} is off.")
            else:
                self.jarvis.say(f"Bulb {ip} is off.")

    def discover(self):
        """
        Filter the respond and keep only the necessary attributes of the light.
        Ip , name (if exists) and rgb capability
        """
        discovered = discover_bulbs()
        for bulb in discovered:
            self.discovered_bulbs[bulb['ip']] = {
                'name': bulb['capabilities']['name'], 'has_rgb': False}
            if 'set_rgb' in bulb['capabilities']['support']:
                self.discovered_bulbs[bulb['ip']]['has_rgb'] = True

    def get_bulb_number(self, upper_bound: int):
        """
        Get user input and validate it.
        Input must be a number that corresponds to an IP.
        """
        input_code = 0
        # Until country code is valid
        if upper_bound > 0:
            input_code = None
            while not input_code:
                try:
                    input_code = self.jarvis.input(
                        f"Choose the number that corresponds to the bulb: ")
                    if self.is_valid_input(int(input_code), upper_bound):
                        raise ValueError
                except ValueError:
                    if self.is_exit_input(input_code):
                        return self.exit_msg
                    self.jarvis.say(
                        f"Please select a number (0 - {upper_bound})", color=Fore.YELLOW)
                    input_code = None
        return int(input_code)

    def validate_name(self):
        """
        Get user input and validate it.
        Bulb name must not be empty or an existing name.
        """
        input_name = ''
        # Until name is valid
        while not input_name:
            try:
                input_name = self.jarvis.input("Please enter a name: ")
                if not self.is_available_name(input_name):
                    raise ValueError
            except ValueError:
                if self.is_exit_input(input_name):
                    return self.exit_msg
                self.jarvis.say("Chosen name is empty or exists. Also tou should use one-word names")
                input_name = ''
        return input_name

    def name_bulbs(self) -> int:
        """
        This method is for naming the user's smart bulbs,
        to be able to controll them with comfort.
        All bulbs should have a name for the user to be
        able to controll them.
        """
        unknown_bulbs = self.find_unknown_bulbs()
        while True:
            self.jarvis.say(f"{len(unknown_bulbs)} unknown bulb(s) found!")
            for count, bulb in enumerate(unknown_bulbs):
                self.jarvis.say(f"{count}. {bulb}")
            if not unknown_bulbs:
                self.jarvis.say("All bulbs are named!", color=Fore.GREEN)
                break
            else:
                input = self.get_bulb_number(len(unknown_bulbs) - 1)
                if self.is_exit_input(input):
                    return self.exit_msg
                else:
                    self.jarvis.say(
                        "The chosen bulb will flash now.", color=Fore.YELLOW)
                    """
					Bulb flashing for the user to identify and
					name it easily
					"""
                    for i in range(3):
                        yeelight.Bulb(unknown_bulbs[input]).turn_off()
                        time.sleep(1)
                        yeelight.Bulb(unknown_bulbs[input]).turn_on()
                        time.sleep(1)
                    name = self.validate_name()
                    yeelight.Bulb(unknown_bulbs[input]).set_name(name)
                    self.discovered_bulbs[unknown_bulbs[input]]['name'] = name
                    unknown_bulbs.pop(input)

    def is_exit_input(self, input) -> bool:
        if (type(input) == str and input.lower() == self.exit_msg):
            return True

    def is_valid_input(self, input, upper_bound) -> bool:
        if type(input) == int and self.is_out_of_range(input, upper_bound):
            return True

    def is_available_name(self, name) -> bool:
        # checks if the name is valid
        if (name != '' and type(name) == str and name.lower() != 'exit' and self.is_valid_name(name) and len(name.strip().split()) == 1):
            return True

    def is_valid_name(self, name) -> bool:
        # checks if the name is already given in another bulb
        for bulb in self.discovered_bulbs:
            if self.discovered_bulbs[bulb]['name'] == name:
                return False
        return True

    def is_out_of_range(self, x: int, upper_bound) -> bool:
        return (True if (x > upper_bound or x <= 0) else False)

    def find_unknown_bulbs(self) -> List:
        return [ip for ip in self.discovered_bulbs if self.discovered_bulbs[ip]['name'] == '']
