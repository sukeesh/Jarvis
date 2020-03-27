from plugin import plugin, require
import requests
import random
import json
from colorama import Fore

@require(network=True)
@plugin('history')
class history:
    """
    Provides you with a random hisotry fact

    Enter 'history' to use:
    * history <event> <day> <month>
    """

    def __init__(self):
        self.url = "http://history.muffinlabs.com/date"
        self.events = ['births', 'deaths', 'events']
        self.months = ['january', 'february', 'march', 'april', 'may', 'june',
                       'july', 'august', 'september', 'october', 'november', 'december']
        self.keywords = ['today']
        self.MAX_LINK = 3

    def __call__(self, jarvis, s):
        if s == 'help':
            self._print_help(jarvis)
            return

        jarvis.say("\ntype 'history help' for additional information")
        config = self._parse_arguments(s)
        api_cfg = self._parse_config(config)
        query = self._generate_query(api_cfg)
        result = self._get_data(jarvis, query, api_cfg)
        if not result:
            return
        self._print_result(jarvis, result)

    # manual for plugin
    def _print_help(self, jarvis):
        jarvis.say("\nWelcome to History!", Fore.CYAN)
        jarvis.say("You can use current plugin as follows:", Fore.CYAN)
        jarvis.say("    history <keyword> <event> <day> <month>", Fore.CYAN)
        jarvis.say("    <keyword> - Program uses special keywords to easily identify your query. keywords:", Fore.CYAN)
        jarvis.say("                * 'today' - results in getting fact that happened on this day", Fore.CYAN)
        jarvis.say("    <event>   - Argument used to specify historical fact type, which can be one of the following:", Fore.CYAN)
        jarvis.say("                * 'births'", Fore.CYAN)
        jarvis.say("                * 'deaths'", Fore.CYAN)
        jarvis.say("                * 'events'", Fore.CYAN)
        jarvis.say("    <month>   - Specify month", Fore.CYAN)
        jarvis.say("    <day>     - Specify day", Fore.CYAN)
        jarvis.say("All of the arguments are optional. Not specifying results in randomization.", Fore.CYAN)
        jarvis.say("Example: ", Fore.CYAN)
        jarvis.say("         'history 25 march birth' - birth of a random person on 25th of March", Fore.CYAN)
        jarvis.say("         'history 10' - random event that happened on random month but day is 10", Fore.CYAN)
        jarvis.say("         'history today' - random type of event that happened on the present day", Fore.CYAN)
        jarvis.say("         'history today events' - event that occured on the present day", Fore.CYAN)


    # parses user given arguments and returns dictionary of configuration
    def _parse_arguments(self, args):
        split_args = args.split()
        cfg = {'event': None, 'month': None, 'day': None, 'keywords': set()}
        
        # iterate over the arguments an fill configurations
        for arg in split_args:
            if arg.isdigit():
                cfg['day'] = arg
            elif arg in self.events:
                cfg['event'] = arg
            elif arg in self.months:
                cfg['month'] = arg
            elif arg in self.keywords:
                cfg['keywords'].add(arg)
        
        return cfg

    # used to further parse given configuration and validate user arguments
    def _parse_config(self, config):
        api_cfg = {}

        # check for today keyword
        api_cfg['today'] = False
        if 'today' in config['keywords']:
            api_cfg['today'] = True

        # check for events
        api_cfg['event'] = config['event']
        if not api_cfg['event']:
            api_cfg['event'] = random.choice(self.events)

        # check for month
        api_cfg['month'] = config['month']
        if not api_cfg['month']:
            api_cfg['month'] = random.choice(self.months)

        # check for day
        api_cfg['day'] = config['day']
        if not api_cfg['day']:
            api_cfg['day'] = random.randint(1, 29)

        return api_cfg

    # generates query to be sent over web to given API
    def _generate_query(self, api_cfg):
        # if one of arguments passed was 'today' return default link
        # (default link returns history facts that happend on current date)
        if api_cfg['today']:
            return self.url

        day = api_cfg['day']
        month = self.months.index(api_cfg['month']) + 1

        # url = api.com/date/<month>/<day>
        query_str = '{}/{}/{}'.format(self.url,  month, day)
        return query_str

    # send request and retrieves data from API
    def _get_data(self, jarvis, query, api_cfg):
        data = None
        try:
            jarvis.spinner_start('Searching through history ')
            # send request
            response = requests.get(query)
            # parse into json
            result = response.json()
            # randomly et one of the facts
            facts_arr = result['data'][api_cfg['event'].capitalize()]
            fact = random.choice(facts_arr)
            # generate data from result
            data = {
                'date': result['date'],
                'type': api_cfg['event'],
                'year': fact['year'],
                'text': fact['text'],
                'links': fact['links']
            }
            jarvis.spinner_stop()
        except:
            jarvis.spinner_stop(message="\nTask execution Failed!", color=Fore.RED)
            jarvis.say("Please check that arguments are correct and day of month is valid!", Fore.RED)
            jarvis.say("If error occures again, then API might have crashed. Try again later.\n", Fore.RED)
        finally:
            return data

    # prints result of query in a human readable way
    def _print_result(self, jarvis, result):
        # first line of output contains date of fact
        jarvis.say('\nDate : {} of {}'.format(result['date'], result['year']), Fore.BLUE)

        # second line contains information
        jarvis.say('{} : {}'.format(result['type'], result['text']), Fore.BLUE)

        # next lines will be links to external sources
        jarvis.say('External links : ', Fore.BLUE)
        result['links'] = result['links'][:self.MAX_LINK]
        for i in range(len(result['links'])):
            jarvis.say('    {}). {}'.format(i+1, result['links'][i]['link']), Fore.BLUE)
