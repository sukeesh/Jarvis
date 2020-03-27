from plugin import plugin, require
import requests
import random
import json


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
        config = self._parse_arguments(s)
        api_cfg = self._parse_config(config)
        query = self._generate_query(api_cfg)
        result = self._get_data(query, api_cfg)
        self._print_result(jarvis, result)

    def _parse_arguments(self, args):
        split_args = args.split()
        cfg = {'event': None, 'month': None, 'day': None, 'keywords': set()}
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

    def _get_data(self, query, api_cfg):
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
        return data

    def _print_result(self, jarvis, result):
        # first line of output contains date of fact
        jarvis.say('Date : {} of {}'.format(result['date'], result['year']))

        # second line contains information
        jarvis.say('{} : {}'.format(result['type'], result['text']))

        # next lines will be links to external sources
        jarvis.say('External links : ')
        result['links'] = result['links'][:self.MAX_LINK]
        for i in range(len(result['links'])):
            jarvis.say('    {}). {}'.format(i+1, result['links'][i]['link']))
