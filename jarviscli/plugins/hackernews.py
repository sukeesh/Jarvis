from typing import List, Tuple, Set
import webbrowser

from bs4 import BeautifulSoup
from colorama import Fore
import requests

from plugin import plugin, alias, require


class HackerNewsRequestException(Exception):
    """Custom exception class for request errors"""


class HackerNewsInvalidInputException(Exception):
    """Custom exception class for invalid inputs"""


@require(network=True)
@alias("readhn")
@plugin("hackernews")
class HackerNews:
    """List titles from https://news.ycombinator.com/

    Selected titles are opened in the browser as separate tabs.
    """

    URL = "https://news.ycombinator.com/"

    def __call__(self, jarvis: "JarvisAPI", s: str) -> None:
        """List titles, get selected titles from user and open them in the browser

        :type jarvis: JarvisAPI
        :param jarvis: JarvisAPI instance
        :type s: str
        :param s: Text to say
        """

        try:
            self.titles = self._list_titles(jarvis)
            selected_titles = self._get_selected_titles(jarvis)
            self._open_selected_titles(selected_titles)

        except (HackerNewsRequestException, HackerNewsInvalidInputException) as exp:
            jarvis.say(str(exp), color=Fore.RED)

    def _list_titles(self, jarvis: "JarvisAPI") -> List[Tuple[str, str]]:
        """List titles

        If any errors are encountered during the request,
        HackerNewsRequestException will be raised.

        :type jarvis: JarvisAPI
        :param jarvis: JarvisAPI instance
        :rtype: list
        :returns: List of titles as (title, link) tuples
        """

        titles = []

        try:
            response = requests.get(self.URL)
            response.raise_for_status()
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.HTTPError,
        ) as exp:
            raise HackerNewsRequestException(exp) from exp
        else:
            parsed_page = BeautifulSoup(response.content, "html.parser")

            title_elements = parsed_page.select("a.titlelink")

            for index, element in enumerate(title_elements, start=1):
                jarvis.say("[{:>2}] {}".format(index, element.getText()))
                titles.append((element.getText(), element["href"]))

        return titles

    def _get_selected_titles(self, jarvis: "JarvisAPI") -> Set[int]:
        """Get selected indexes from user

        If there is no index selected or indexes are in the invalid range,
        HackerNewsInvalidInputException will be raised.

        :type jarvis: JarvisAPI
        :param jarvis: JarvisAPI instance
        :rtype: set
        :returns: Set of selected indexes
        """

        indexes = jarvis.input(
            prompt="\nEnter requested title indexes: ", color=Fore.YELLOW
        )

        selected_indexes = [int(index) for index in indexes.split() if index.isdigit()]

        if not selected_indexes:
            raise HackerNewsInvalidInputException("No index selected!")

        for index in selected_indexes:
            if not 1 <= index <= 30:
                raise HackerNewsInvalidInputException(
                    "Invalid index! Should be in range 1..30"
                )

        return set(selected_indexes)

    def _open_selected_titles(self, selected_titles: Set[int]) -> None:
        """Open selected titles in the browser as new tabs

        :type selected_titles: set
        :param selected_titles: Set of indexes
        """

        for index in selected_titles:
            link = self.titles[index - 1][1]

            # add root url for internal links
            if "item?" in link:
                link = self.URL + link

            webbrowser.open_new_tab(link)
