# Modules
# Webscrapping
import requests
from bs4 import BeautifulSoup
# Jarvis
from colorama import Fore
from plugin import plugin, require


@require(network=True)
@plugin('market find')
def market_search(jarvis, s):
    """Search Github Topics (a.k.a. market) to find baskets
    (single or bunch of plugins together).

    Check the PLUGIN_MARKETPLACE.md for more information.

    Args:
    * n:
    You can use the "n=" or "n =" argument to delimit the number of
    repository shown. Ex: "market find n=15"
    """
    # Downloading page
    URL = 'https://github.com/topics/jarvis-plugins'
    page = requests.get(URL)

    # Inserting into the Beautiful Soup framework
    soup = BeautifulSoup(page.content, 'html.parser')

    # Finding all the links
    links_repos_objs = soup.find_all('a', class_='text-bold')
    repo_links = [repo_link['href'] for repo_link in links_repos_objs]

    # Listing all baskets
    jarvis.say('Searching..')
    n_limit = parse_items_limit(s)
    # For changing colours
    colour_number = 1
    for index, link in enumerate(repo_links):
        if index >= n_limit:
            break
        # Removing initial '/'
        link = link[1:]
        # Changing colour pattern
        if colour_number == 1:
            colour = Fore.BLUE
            colour_number = 0
        else:
            colour = Fore.GREEN
            colour_number = 1

        jarvis.say(link, colour)


def parse_items_limit(text, default=10):
    """If the user provides the argument 'n=...'
    It will be used to delimit the number of repositories shown.
    """
    which_arg_used = [i for i in ['n=', 'n ='] if i in text]
    if len(which_arg_used) == 0:
        return default
    else:
        text = text.replace(which_arg_used[0], '').replace(' ', '')

    return int(text)
