import secrets
import string
from plugin import plugin, require, alias

@require(network=False)
@alias("generate password")
@plugin("password generator")
class PasswordGenerator:
    """
    This plugin generates a strong, random password with a specified length and choice of character types:
    uppercase, lowercase, digits, and special characters.
    """

    def __call__(self, jarvis, s):
        self.generate_password(jarvis)

    def generate_password(self, jarvis):
        jarvis.say("Welcome to the Password Generator!")
        length = jarvis.input_number("Enter the desired password length (minimum 12): ", rtype=float)
        if length is None or length < 12:
            jarvis.say("Invalid length. Password length must be at least 12 characters for security.")
            return
        
        include_uppercase = jarvis.ask_yes_no("Include uppercase letters (A-Z)? (yes/no): ")
        include_lowercase = jarvis.ask_yes_no("Include lowercase letters (a-z)? (yes/no): ")
        include_digits = jarvis.ask_yes_no("Include digits (0-9)? (yes/no): ")
        include_specials = jarvis.ask_yes_no("Include special characters (e.g., @#$%)? (yes/no): ")

        if not any([include_uppercase, include_lowercase, include_digits, include_specials]):
            jarvis.say("At least one character type must be selected!")
            return

        password = self.create_password(int(length), include_uppercase, include_lowercase, include_digits, include_specials)
        jarvis.say(f"Generated Password: {password}", color='green')

    def create_password(self, length, include_uppercase, include_lowercase, include_digits, include_specials):
        char_pool = []
        if include_uppercase:
            char_pool.append(string.ascii_uppercase)
        if include_lowercase:
            char_pool.append(string.ascii_lowercase)
        if include_digits:
            char_pool.append(string.digits)
        if include_specials:
            char_pool.append(string.punctuation)

        if not char_pool:
            return ''

        # Ensuring each character type selected is used at least once
        password_chars = [secrets.choice(chars) for chars in char_pool]
        password_chars += [secrets.choice(''.join(char_pool)) for _ in range(length - len(password_chars))]

        secrets.SystemRandom().shuffle(password_chars)  # Use SystemRandom for better entropy
        return ''.join(password_chars)
