import webbrowser
import os
import socket
from urllib.parse import urlparse
from plugin import plugin, alias, require

FILE_PATH = os.path.abspath(os.path.dirname(__file__))


@require(network=True)
@alias("visit website")
@plugin("website")
class OpenWebsite:
    """
    This plugin will visit a website using some parameters.

    The user can visit a simple website giving a complete link or
    inputting the name of the website like the examples:

    > visit website www.google.com
    > visit website github
    > visit website github username

    You can find a csv file with a list of saved websites at:
    Jarvis/jarviscli/data/website.csv

    {Alternatively, you can also use only 'website'
    instead of 'visit website'}
    """

    def __call__(self, jarvis, link):
        inputs = link.split(' ')
        self.main_link = inputs[0]
        self.complement = False
        if len(inputs) > 1:
            self.complement = inputs[1]

        if self.has_on_saved_links():
            webbrowser.open(self.main_link)
        elif self.verify_link():
            webbrowser.open(self.main_link)
        else:
            jarvis.say("Sorry, I can't open this link.")

    def has_on_saved_links(self):
        websites_csv = \
            open(os.path.join(FILE_PATH, "../data/websites.csv"), 'r')
        for website in websites_csv:
            website = website.rstrip()  # remove newline
            information = website.split(',')
            if self.main_link == information[0]:
                if self.complement:
                    if len(information) > 2:
                        self.main_link = \
                            information[1] + information[2] + self.complement
                    else:
                        self.main_link = information[1] + self.complement
                else:
                    self.main_link = information[1]
                return True

        return False

    def verify_link(self):
        self.fix_link()

        domain = urlparse(self.main_link).netloc
        try:
            socket.getaddrinfo(domain, 80)
        except socket.gaierror:
            return False

        return True

    def fix_link(self):
        if not self.main_link.startswith('http'):
            self.main_link = "https://" + self.main_link
