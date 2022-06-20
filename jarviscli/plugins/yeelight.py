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


	def main(self):
		self.jarvis.say("To exit enter word 'exit'", color=Fore.YELLOW)
		# Find the connected bulbs to the router		
		self.discover()
		# We can not continue if the bulbs has not a name to reference them.
		if self.find_unknown_bulbs():
			self.name_bulbs()
		

	def discover(self):
		"""
		Filter the respond and keep only the necessary attributes of the light.
		Ip , name (if exists) and rgb capability
		"""
		discovered = discover_bulbs()
		for bulb in discovered:
			self.discovered_bulbs[bulb['ip']] = {'name': bulb['capabilities']['name'], 'has_rgb': False}
			if 'set_rgb' in bulb['capabilities']['support']:
				self.discovered_bulbs[bulb['ip']]['has_rgb'] = True
	
	def get_bulb_number(self, upper_bound: int):

	def validate_name(self):
		"""
		Get user input and validate it.
		Bulb name must not be empty or an existing name.
		"""
		input_name = ''
		#Until name is valid
		while not input_name:
			try:
				input_name = self.jarvis.input("Please enter a name:")
				if self.is_available_name(input_name):
					raise ValueError
			except ValueError:
				if self.is_exit_input(input_name):
					return self.exit_msg
				self.jarvis.say("Chosen name is empty or exists.")
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
					self.jarvis.say("The chosen bulb will flash now.", color=Fore.YELLOW)
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
	
	def is_available_name(self, name) -> bool:
		# checks if the name is valid
		if name and type(name) == str and self.is_valid_name(name):
			return True
	
	def is_valid_name(self, name) -> bool:
		# checks if the name is already given in anothe bulb
		for bulb in self.discovered_bulbs:
			if self.discovered_bulbs[bulb]['name'] == name:
				return False
		