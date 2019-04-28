from plugin import plugin, require
import webbrowser


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

        validated_link = self.verify_link(main_link)

        if self.has_on_links_dictionary(main_link):
            webbrowser.open(self.links_dictionary.get(main_link) + complement)
        elif validated_link:
            validated_link = self.fix_link(validated_link)
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

        if link[:3] == "www":
            link = "http://" + link
        return link

    def has_on_links_dictionary(self, link):
        return link in self.links_dictionary

    def start_links_dictionary(self):
        self.links_dictionary['github'] = "https://github.com/"
        self.links_dictionary['facebook'] = "https://www.facebook.com/"
        self.links_dictionary['linkedin'] = "https://www.linkedin.com/in/"
        self.links_dictionary['medium'] = "https://medium.com/@"
        self.links_dictionary['twitter'] = "https://twitter.com/"
        self.links_dictionary['instagram'] = "https://www.instagram.com/"

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

        # TODO create a list with all possibles terminations of link
        #  ['com','net',...]
        if "com" in link:
            links = link.split('com', 1)
            link = links[0] + '.com' + links[1]

        return link
