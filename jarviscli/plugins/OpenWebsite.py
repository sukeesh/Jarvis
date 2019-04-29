import webbrowser
import os
from plugin import plugin, require

FILE_PATH = os.path.abspath(os.path.dirname(__file__))


@require(network=True)
@plugin("open website")
class OpenWebsite:
    """
    This plugin will open a website using some params.

    The user can open a simple website giving a complete link or
    inputting the name of the website like the examples:

    > open website www.google.com
    > open website github
    > open website github username
    """
    def __call__(self, jarvis, link):
        inputs = link.split(' ', 1)
        main_link = inputs[0]
        complement = ""
        if len(inputs) > 1:
            complement = inputs[1]

        self.links_dictionary = {}

        # TODO create a cache for this
        self.start_links_dictionary()

        if self.has_on_links_dictionary(main_link):
            webbrowser.open(self.links_dictionary.get(main_link) + complement)
        elif self.verify_link(main_link):
            validated_link = self.fix_link(main_link)
            webbrowser.open(validated_link)
            pass
        else:
            print("Sorry, I can't open this link please try again.")

    def verify_link(self, link):
        if ((link[:8] != "https://" and
             link[:7] != "http://" and
             link[:3] != "www") or
                ("com" not in link)):
            return False

        return True

    def fix_link(self, link):
        """
        When the links come as input they come without '.'
        > open website www.google.com
        What I get here:
        wwwgooglecom

        So this function get the link without '.' and add the '.'
        """
        if "www" in link:
            links = link.split('www', 1)
            link = links[0] + 'www.' + links[1]

        if link[:3] == "www":
            link = "http://" + link

        if "com" in link:
            splited_link = link.split('com', 1)
            link = ""
            for index in range(len(splited_link) - 1):
                link += splited_link[index]

            link += ".com" + splited_link[len(splited_link) - 1]

        return link

    def start_links_dictionary(self):
        websites_csv = \
            open(os.path.join(FILE_PATH, "../data/websites.csv"), 'r')
        for website in websites_csv:
            information = website.split(',', 1)
            self.links_dictionary[information[0]] = information[1]

    def has_on_links_dictionary(self, link):
        return link in self.links_dictionary
