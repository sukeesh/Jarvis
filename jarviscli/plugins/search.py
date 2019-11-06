import webbrowser
from plugin import require, plugin


@require(network=True)
@plugin("search")
class Search:
    """
    The 'search' command launches a browser search
    for the entered keywords.

    To search in a new tab in an existing browser window, write:
    'search new_tab <keywords>'
    (If there is no existing window, new window is opened.)

    {Just write the keywords as you would in the google search bar.}

    Examples:
    > search how to clone a github repository
    > search new_tab linux distros
    """

    def __call__(self, jarvis, s):
        self.command = s
        self.new_tab = True
        self.check_new_tab()
        self.create_link()
        self.open_browser()

    def check_new_tab(self):
        if "new_tab" in self.command:
            self.inputs = self.command.split(' ', 1)
            self.keyword_str = self.inputs[1]
        else:
            self.keyword_str = self.command
            self.new_tab = False

    def create_link(self):
        self.default = "https://www.google.com/search?q="
        self.keywords = self.keyword_str.replace(' ', '+').strip()
        # strip To remove whitespaces
        self.link = self.default + self.keywords

    def open_browser(self):
        if self.new_tab is False:
            # Opens search results in a new browser window.
            webbrowser.open_new(self.link)
        else:
            # Opens search results in a new tab.
            webbrowser.open_new_tab(self.link)
