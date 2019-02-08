# !!! This uses the https://newsapi.org/ api. TO comply with the TOU
# !!! we must link back to this site whenever we display results.
try:  # python3
    import urllib.request
    import urllib.parse
    import urllib.error
except ImportError:  # python2
    import urllib
import json
import webbrowser
from six.moves import input
from plugin import Plugin
from colorama import Fore

'''
    CLASS News
    To run the full news class run:
        news_options
        THEN
        get_news
    For quick news run:
        request_news

    example:
    n = News()
    n.news()
    OR
    n = News()
    n.quick_news()
'''


class News(Plugin):
    """
    Time to get an update about the local news.
    Type \"news\" to choose your source or \"news quick\" for some headlines.
    """
    def __init__(self, source="google-news", api_key="7488ba8ff8dc43459d36f06e7141c9e5"):
        self.apiKey = api_key
        self.source = source
        self.url = "https://newsapi.org/v1/articles?source=google-news&sortBy=top" \
                   "&apiKey=7488ba8ff8dc43459d36f06e7141c9e5"
        self.is_news_site_configured = False

    def require(self):
        yield ("network", True)

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        if s == "quick":
            try:
                self.quick_news()
            except:
                jarvis.say("I couldn't find news", Fore.RED)
        else:
            try:
                if jarvis.get_data('news-settings') is not None and len(jarvis.get_data('news-settings')) > 0:
                    self.is_news_site_configured = True
                self.news(jarvis)
            except:
                jarvis.say("I couldn't find news", Fore.RED)

    @staticmethod
    def get_key():
        return "news-settings"

    def check_newsapi_url(self, site_key):
        url = "https://newsapi.org/v1/articles?source=" + \
            site_key + "&sortby=top&apiKey=" + self.apiKey
        try:
            try:
                response = urllib.request.urlopen(url)
            except urllib.error.HTTPError:
                return False
        except AttributeError:
            response = urllib.urlopen(url)
        if response.code >= 400:
            return False
        else:
            return True

    def news(self, jarvis):
        print('Would you like to configure your own news channel(y/n)')
        i = str(input())
        if i.lower() == "y":
            self.configure_news_site(jarvis)
        else:
            self.news_options(jarvis)
            self.get_news()

    '''
        This is the quickest way to get news it also has the
        least amount of options for the user.
    '''

    def configure_news_site(self, jarvis):
        news_site_list = jarvis.get_data(News.get_key())
        # Check if no sites are configured
        if news_site_list is None:
            news_site_list = []
        print("List of configured news sites are as below")
        for idx, site in enumerate(news_site_list):
            print("{} : {}".format(idx + 1, site))

        print("Search https://newsapi.org/sources for the list of news channels. Enter site-key")
        site_key = str(input())
        if site_key is '':
            print("Wrong input.")
        elif site_key in news_site_list:
            print("Site already added. Hence not updating the list.")
        elif self.check_newsapi_url(site_key) is False:
            print("News source {} doesn't exist".format(site_key))
        else:
            news_site_list.append(site_key)
            self.is_news_site_configured = True

        print("List of configured news sites are as below")

        for idx, site in enumerate(news_site_list):
            print("{} : {}".format(idx + 1, site))

        print("Would you like to delete any in the list?(y/n)")
        del_from_list = str(input())
        if del_from_list.lower() == "y":
            print("Enter the site index to be deleted. If multiple sites, then enter index with comma seperated values")
            index_to_del = str(input())
            items_idx_to_del = index_to_del.split(',')
            list_to_del = [news_site_list[int(item) - 1] for item in items_idx_to_del]
            news_site_list = [item for item in news_site_list if item not in list_to_del]
            if len(news_site_list) == 0:
                self.is_news_site_configured = False
        jarvis.update_data(News.get_key(), news_site_list)
        self.news_options(jarvis)
        self.get_news()

    def quick_news(self):
        self.request_news()
    '''
        Gets and returns JSON data of news
    '''

    def get_news_json(self):
        try:
            response = urllib.request.urlopen(self.url)
        except AttributeError:
            response = urllib.urlopen(self.url)
        return json.loads(response.read().decode('utf-8'))

    '''
        This sets the users options and loads them from Memory
        if they exist
    '''

    def news_options(self, jarvis):
        # check to see if user already has default news source
        if jarvis.get_data('news-source'):
            print("your default news source is {}"
                  .format(jarvis.get_data('news-source')))
            print("Would you like news from this source? (yes/no): ")
            x = input()
            if x == 'y' or x == 'yes':
                self.source = jarvis.get_data('news-source')
            # if news site configured already, display it
            elif self.is_news_site_configured:
                get_configured_opt(jarvis)
            # if not set get users preference
            else:
                self.get_default_opt(jarvis)
        elif self.is_news_site_configured:
            self.get_configured_opt(jarvis)
        else:
            self.get_default_opt(jarvis)

    def get_configured_opt(self, jarvis):
        news_site_list = jarvis.get_data('news-settings')
        print('Selec Source : ')
        for idx, site in enumerate(news_site_list):
            print("{}:{}".format(idx + 1, site))
        i = int(input())
        self.source = news_site_list[i - 1]

    def get_default_opt(self, jarvis):
        # Other sources available here: https://newsapi.org/sources
        print("Select Source (1-5):")
        print("1: BBC")
        print("2: BUZZFEED")
        print("3: Google")
        print("4: Reddit")
        print("5: TechCrunch")

        i = int(input())
        if i == 1:
            self.source = "bbc-news"
        elif i == 2:
            self.source = "buzzfeed"
        elif i == 3:
            self.source = "google-news"
        elif i == 4:
            self.source = "reddit-r-all"
        elif i == 5:
            self.source = "techcrunch"

        print("would you like to set this as your default? (yes/no): ")
        x = input()
        if x == 'y' or x == 'yes':
            jarvis.update_data('news-source', self.source)  # save to memory

    '''
        This sets the url and sends it to request_news()
    '''

    def get_news(self):
        u = "https://newsapi.org/v1/articles?source=" + \
            self.source + "&sortby=top&apiKey=" + self.apiKey
        self.request_news(u)

    '''
        This has all the logic to request and parse the json.
        This function DOES NOT check user preferences.
        It also includes user interactions for getting more info on an articles
    '''

    def request_news(self, url=None):
        # check to see if a url was passed
        if url is None:
            url = self.url
        try:
            response = urllib.request.urlopen(url)
        except AttributeError:
            response = urllib.urlopen(url)
        # Load json
        data = json.loads(response.read())
        article_list = {}
        index = 1
        # print articles with their index
        print("Top News Articles from " + self.source)
        for article in data['articles']:
            # print (Fore.GREEN + str(index) + ": " + article['title'] + Fore.RESET)
            print(str(index) + ": " + article['title'])
            article_list[index] = article
            index += 1

        # Attribution link for News API to comply with TOU
        print("Powered by News API. Type NewsAPI to learn more")
        print("Type index to expand news\n")

        # Check to see if index or NewsAPI was enterd
        idx = input()
        if idx.lower() == "newsapi":
            webbrowser.open('https://newsapi.org/')
            return

        # check if we have a valid index
        try:
            int(idx)
            if int(idx) > index:
                print("Not a valid index")
                return
        except:
            print("Not a valid index")
            return

        # if index valid print article description
        print(article_list[int(idx)]['description'])

        print("Do you want to read more? (yes/no): ")
        i = input()
        # if user wants to read more open browser to article url
        if i.lower() == "yes" or i.lower() == 'y':
            webbrowser.open(article_list[int(idx)]['url'])
            return
        else:
            return
