from colorama import Fore
import requests


def main(self):
    try:
        req = requests.get("https://api.chucknorris.io/jokes/random")
        chuck_json = req.json()

        chuck_fact = chuck_json["value"]
        if self.enable_voice:
            print(Fore.RED + chuck_fact + Fore.RESET)
            self.speech.text_to_speech(chuck_fact)
        else:
            print(Fore.RED + chuck_fact + Fore.RESET)
    except:
        if self.enable_voice:
            self.speech.text_to_speech(
                "Looks like Chuck broke the Internet.")
        else:
            print(
                Fore.RED +
                "Looks like Chuck broke the Internet..." + Fore.RESET)
