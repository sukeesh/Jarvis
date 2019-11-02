from plugin import plugin, require
import webbrowser
from colorama import Fore


@require(network=True)
@plugin('browser')
def browser(jarvis, s):
    """Command 'browser' opens Google search in a new browser window.
    To open a new tab in an existing browser window, write:
    'browser new_tab'
    (If there is no existing window, new window is opened.)
    """

    if ("new_tab" in s):
        # Opens Google search in a new tab
        webbrowser.open_new_tab('https://www.google.com')
        jarvis.say("Opened new tab in existing browser window.", Fore.BLUE)

    else:
        # Opens Google search in a new browser window.
        webbrowser.open_new('https://www.google.com')
        jarvis.say("Opened new browser window.", Fore.BLUE)
