Documentation for passGen.py
Overview
passGen.py contains a class PasswordGenerator designed for Jarvis, a plugin-based command-line tool. This plugin allows users to generate strong, random passwords directly through the command line interface. It supports various customizable parameters such as password length and character types including uppercase, lowercase, digits, and special characters.

Requirements
Python 3.6+
The Jarvis command line interface setup
secrets and string libraries (standard in Python 3.6+)
Installation
No additional installation is necessary beyond setting up the Jarvis framework and ensuring that Python 3.6 or newer is installed on your system. Simply place passGen.py in the Jarvis plugins directory, typically found at jarviscli/plugins.

Usage
To use the PasswordGenerator plugin, ensure it is loaded in the Jarvis framework, and initiate it through the Jarvis command line interface with the following command:

generate password
This will activate the plugin and start the password generation process.

Class and Methods
PasswordGenerator

Purpose: Provides functionalities to generate a secure, random password based on user-specified criteria.
Methods:
__call__(self, jarvis, s): Entry point method called by the Jarvis framework when the plugin is activated. It delegates the main operation to generate_password.
generate_password(self, jarvis): Interacts with the user to specify password criteria and initiates the password creation process.
create_password(self, length, include_uppercase, include_lowercase, include_digits, include_specials): Constructs a password based on specified parameters ensuring randomness and security through cryptographic methods.
Detailed Method Description
generate_password(self, jarvis)

Parameters:
jarvis: Instance of JarvisAPI, used to interact with the user.
Functionality:
Prompts the user for the desired password length and character types.
Validates the user inputs and ensures security standards are met.
Calls create_password to generate the password and outputs the result.
create_password(self, length, include_uppercase, include_lowercase, include_digits, include_specials)

Parameters:
length (int): The desired length of the password.
include_uppercase (bool): Whether to include uppercase letters.
include_lowercase (bool): Whether to include lowercase letters.
include_digits (bool): Whether to include numeric digits.
include_specials (bool): Whether to include special characters.
Functionality:
Builds a character pool from the selected character types.
Ensures that each selected character type is represented at least once.
Randomly constructs the password from the character pool using cryptographically secure methods and shuffles it for additional randomness.
Returns the generated password.
Notes
This plugin uses the secrets module for secure random number generation, suitable for cryptographic use, ensuring that the generated passwords are both strong and secure.

Example
To generate a password with all character types, 20 characters long:

generate password
Follow the prompts to specify length and character inclusions.
