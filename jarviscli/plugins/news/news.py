# !!! This uses the https://newsapi.org/ api. TO comply with the TOU
# !!! we must link back to this site whenever we display results.
import json
import webbrowser

import requests
from colorama import Fore

from plugin import plugin, require

SOURCES = [
    'bloomberg',
    'financial-times',
    'cnbc',
    'reuters',
    'al-jazeera-english',
    'the-wall-street-journal',
    'the-huffington-post',
    'business-insider',
    'the-new-york-times',
    'abc-news',
    'fox-news',
    'cnn',
    'google-news',
    'wired']
SOURCE_DICT = {}

for source in SOURCES:
    SOURCE_DICT[str(SOURCES.index(source) + 1)] = source


def get_news_sources(jarvis):
    """
        returns a list of all the new sources added to the news channel of the user
    """
    sources = jarvis.get_data("news-sources")
    if sources is None:
        sources = []
    return sources


@require(network=True, api_key='newsapi_org')
@plugin('news')
def news(jarvis, s, newsapi_org=None):
    def get_headlines():
        """
            gets top headlines for a quick lookup of the world news, based on the news channel of the user (if it exists)
        """
        sources = get_news_sources(jarvis)

        if len(sources) == 0:
            jarvis.say(
                "You have not configured any source. Getting top headlines\n",
                Fore.GREEN)
            url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=" + newsapi_org
        else:
            url = "https://newsapi.org/v2/top-headlines?sources="
            for source in sources:
                url += source + ","
            url += "&apiKey=" + newsapi_org
        return _get(url)

    def get_news(searchlist):
        """
            gets top news based on a particular search list , based on the news channel of the user (if it exists)
        """
        sources = get_news_sources(jarvis)

        url = "https://newsapi.org/v2/everything?q="

        for i in searchlist:
            url += i + "%20"
        if len(sources) != 0:
            url += "&sources="
            for source in sources:
                url += source + ","
        url += "&apiKey=" + newsapi_org
        return _get(url)

    def _get(url):
        """fetch a webpage"""
        response = requests.get(url)
        if response.status_code == requests.codes.ok:
            data = json.loads(response.text)
            return data
        else:
            if response.status_code == 401:
                jarvis.say("API key not valid", Fore.RED)
            else:
                jarvis.say("An error occured: Error code: "
                           + response.raise_for_status(), Fore.RED)
            return None

    def parse_articles(data):
        article_list = {}
        index = 1
        if data is None:
            jarvis.say("No Articles", Fore.RED)
            return
        # jarvis.say articles with their index
        if not data['articles']:
            jarvis.say("No Articles matching the word(s)", Fore.RED)
            return
        for article in data['articles']:
            jarvis.say(str(index) + ": " + article['title'])
            article_list[index] = article
            index += 1

        # Attribution link for News API to comply with TOU
        jarvis.say("\nPowered by News API. Type NewsAPI to learn more")
        jarvis.say("\nType index to expand news, 0 to return to jarvis prompt\n")

        # Check to see if index or NewsAPI was enterd
        idx = jarvis.input()
        if idx.lower() == "newsapi":
            webbrowser.open('https://newsapi.org/')
            return

        # check if we have a valid index
        try:
            int(idx)
            if int(idx) > (index - 1):
                jarvis.say(str(idx) + " is not a valid index", Fore.RED)
                return
            elif int(idx) == 0:
                return
        except BaseException:
            jarvis.say("Not a valid index", Fore.RED)
            return

        # if index valid jarvis.say article description
        jarvis.say(article_list[int(idx)]['description'])

        jarvis.say("Do you want to read more? (yes/no): ")
        i = jarvis.input()
        # if user wants to read more open browser to article url
        if i.lower() == "yes" or i.lower() == 'y':
            webbrowser.open(article_list[int(idx)]['url'])

    if s == "" or s == " ":
        parse_articles(get_headlines())
    else:
        searchlist = s.split(" ")
        if "" in searchlist:
            searchlist.remove("")
        if " " in searchlist:
            searchlist.remove(" ")
        parse_articles(get_news(searchlist))


@require(network=True, api_key='newsapi_org')
@plugin('news configure')
def news_configure(jarvis, s, newsapi_org=None):
    def add_source(news_source):
        sources = get_news_sources(jarvis)
        if news_source not in sources:
            sources.append(news_source)
            jarvis.update_data("news-sources", sources)
            jarvis.say(
                news_source
                + " has been successfully been added to your sources!",
                Fore.GREEN)
        else:
            jarvis.say(
                news_source
                + " was already included in your sources!",
                Fore.GREEN)
        jarvis.eval('news sources')

    for index in sorted([int(x) for x in SOURCE_DICT.keys()]):
        jarvis.say(str(index) + ": " + SOURCE_DICT.get(str(index)))
    index_list = jarvis.input(
        "Type the indexes of the sources you would like to add to your channel separated by "
        "space: ")
    index_list = index_list.split(" ")
    if " " in index_list:
        index_list.remove(" ")
    if "" in index_list:
        index_list.remove("")
    for index in index_list:
        if index in SOURCE_DICT.keys():
            add_source(SOURCE_DICT.get(index, index))
        else:
            jarvis.say(index + " is not a valid index", Fore.RED)


@require(network=True, api_key='newsapi_org')
@plugin('news remove')
def news_remove(jarvis, s, newsapi_org=None):
    sources = get_news_sources(jarvis)

    dic = {}
    for source in sources:
        dic[str(sources.index(source) + 1)] = source

    for index in sorted([int(x) for x in dic.keys()]):
        jarvis.say(str(index) + " : " + dic[str(index)])
    index_list = jarvis.input(
        "Type the indexes of the sources you would like to remove from your channel separated by "
        "space: ")
    index_list = index_list.split(" ")
    if " " in index_list:
        index_list.remove(" ")
    if "" in index_list:
        index_list.remove("")
    for index in index_list:
        if str(index) in dic:
            source = dic[str(index)]
            sources.remove(source)
            jarvis.update_data("news-sources", sources)
            jarvis.say(
                source
                + " has been successfully removed from your news channel!",
                Fore.GREEN)
        else:
            jarvis.say("Index not found!", Fore.RED)
    jarvis.eval('news sources')


@require(network=True, api_key='newsapi_org')
@plugin('news sources')
def news_sources(jarvis, s, newsapi_org=None):
    sources = get_news_sources(jarvis)
    if not sources:
        jarvis.say(
            "No sources configured. Use 'news configure' to add sources.",
            Fore.RED)
    else:
        dic = {}
        for source in sources:
            dic[str(sources.index(source) + 1)] = source

        for index in sorted([int(x) for x in dic.keys()]):
            jarvis.say(str(index) + " : " + dic[str(index)])
