import requests
from colorama import Fore
from plugin import plugin

@plugin("password generator")
def password_generator(jarvis, s):
    """Generates a password based on user-specified options using API Ninjas"""

    try:
        jarvis.say("Welcome to the Password Generator!", Fore.BLUE)

        # Get the desired length of the password
        while True:
            length_input = jarvis.input("Enter the desired length of the password: ", Fore.YELLOW).strip()
            if length_input.isdigit():
                length = int(length_input)
                break
            else:
                jarvis.say("Invalid input. Please enter a valid number for the length.", Fore.RED)

        # Ask if numbers should be excluded
        while True:
            exclude_numbers_input = jarvis.input("Exclude numbers? (Y/N): ", Fore.YELLOW).strip().lower()
            if exclude_numbers_input in ['y', 'n']:
                exclude_numbers = exclude_numbers_input == 'y'
                break
            else:
                jarvis.say("Invalid input. Please enter 'Y' or 'N'.", Fore.RED)

        # Ask if special characters should be excluded
        while True:
            exclude_special_chars_input = jarvis.input("Exclude special characters? (Y/N): ", Fore.YELLOW).strip().lower()
            if exclude_special_chars_input in ['y', 'n']:
                exclude_special_chars = exclude_special_chars_input == 'y'
                break
            else:
                jarvis.say("Invalid input. Please enter 'Y' or 'N'.", Fore.RED)

        # API URL with parameters
        api_url = 'https://api.api-ninjas.com/v1/passwordgenerator?length={}&exclude_numbers={}&exclude_special_chars={}'.format(
            length, exclude_numbers, exclude_special_chars
        )

        # API request with API key
        response = requests.get(api_url, headers={'X-Api-Key': '1Qt7QsAeXgXjOonxgMlaKQ==bv6Et3TdqFmYsOje'})

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            password = data.get('random_password')
            if password:
                jarvis.say(f"Generated Password: {password}", Fore.GREEN)
            else:
                jarvis.say("Error: Password not generated.", Fore.RED)
        else:
            jarvis.say("Error: Unable to reach the password generator service.", Fore.RED)

    except Exception as e:
        jarvis.say("An error occurred while generating the password.", Fore.RED)