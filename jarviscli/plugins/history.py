import datetime
import random

import requests
from colorama import Fore

from plugin import plugin, require


@require(network=True)
@plugin('history')
class history:
    """
    Provides you with a random hisotry fact

    Enter 'history' to use:
    * history <event> <day> <month>

    Attribution:
        Data taken from wikipedia (CC BY-SA 3.0) with use of http://history.muffinlabs.com
    """
    class KW:
        """ Inner Class for Constants """
        EVENT = 'event'
        DAY = 'day'
        MONTH = 'month'
        KEYWORD = 'keyword'

        DATE_YESTERDAY = 'yesterday'
        DATE_TODAY = 'today'
        DATE_TOMORROW = 'tomorrow'

        ERROR = 'err'

    def __init__(self):
        self.url = "http://history.muffinlabs.com/date"
        self.events = ['births', 'deaths', 'events']
        self.months = ['january', 'february', 'march', 'april', 'may', 'june',
                       'july', 'august', 'september', 'october', 'november', 'december']
        self.keywords = [self.KW.DATE_YESTERDAY,
                         self.KW.DATE_TODAY, self.KW.DATE_TOMORROW]
        self.MAX_LINK = 3
        self.err_cfg_str = 'Error : Please pass only one argument of type {}'

    def __call__(self, jarvis, s):
        if s == 'help':
            self._print_help(jarvis)
            return

        jarvis.say("\ntype 'history help' for additional information")
        # parse and validate arguments
        config = self._parse_arguments(s)
        if config[self.KW.ERROR]:
            jarvis.say(config[self.KW.ERROR], Fore.RED)
            return
        # translate configurations to API recognizable
        api_cfg = self._parse_config(config)
        # query to be sent to API
        query = self._generate_query(api_cfg)
        # fetch result
        result = self._get_data(jarvis, query, api_cfg)
        if not result:
            return
        # output data
        self._print_result(jarvis, result)

    # manual for plugin
    def _print_help(self, jarvis):
        jarvis.say("\nWelcome to History!", Fore.CYAN)
        jarvis.say("You can use current plugin as follows:", Fore.CYAN)
        jarvis.say("    history <keyword> <event> <day> <month>", Fore.CYAN)
        jarvis.say(
            "    <keyword> - Program uses special keywords to easily identify your query. keywords:", Fore.CYAN)
        jarvis.say(
            "                * 'yesterday' - results in getting fact that happened day before today", Fore.CYAN)
        jarvis.say(
            "                * 'today' - results in getting fact that happened on this day", Fore.CYAN)
        jarvis.say(
            "                * 'tomorrow' - results in getting fact that happened day after today", Fore.CYAN)
        jarvis.say(
            "    <event>   - Argument used to specify historical fact type, which can be one of the following:", Fore.CYAN)
        jarvis.say("                * 'births'", Fore.CYAN)
        jarvis.say("                * 'deaths'", Fore.CYAN)
        jarvis.say("                * 'events'", Fore.CYAN)
        jarvis.say("    <month>   - Specify month", Fore.CYAN)
        jarvis.say("    <day>     - Specify day", Fore.CYAN)
        jarvis.say(
            "All of the arguments are optional. Not specifying results in randomization.", Fore.CYAN)
        jarvis.say("Example: ", Fore.CYAN)
        jarvis.say(
            "         'history 25 march birth' - birth of a random person on 25th of March", Fore.CYAN)
        jarvis.say(
            "         'history 10' - random event that happened on random month but day is 10", Fore.CYAN)
        jarvis.say(
            "         'history today' - random type of event that happened on the present day", Fore.CYAN)
        jarvis.say(
            "         'history tomorrow events' - event that occured on the day after today", Fore.CYAN)

    # function that maps shortened string to month
    # example : 'jan'->'januray', 'decem'->'december', 'github'->None
    def _identify_month(self, string):
        # if length of string is less than 3 we will not be able to identify
        # for example 'ju' can map to both 'june' and 'july'
        if len(string) < 3:
            return None

        # iterate over each month and try to find such month that contains our string
        # and also starts with it
        for month in self.months:
            if (string in month) and (month.index(string) == 0):
                return month
        return None

    # parses user given arguments and returns dictionary of configuration
    def _parse_arguments(self, args):
        # validation of arguments
        def __validate(main_event_type, value, cfg, validation_arr=[]):
            validation_arr += [main_event_type]
            for event_type in validation_arr:
                if cfg[event_type] is not None:
                    cfg[self.KW.ERROR] = self.err_cfg_str.format(event_type)
                    return False
            cfg[main_event_type] = value
            return True

        split_args = args.split()
        cfg = {self.KW.EVENT: None, self.KW.MONTH: None,
               self.KW.DAY: None, self.KW.KEYWORD: None, self.KW.ERROR: None}

        # iterate over the arguments an fill configurations
        for arg in split_args:
            if arg.isdigit():
                if not __validate(self.KW.DAY, arg, cfg, [self.KW.KEYWORD]):
                    return cfg
            elif arg in self.events:
                if not __validate(self.KW.EVENT, arg, cfg):
                    return cfg
            elif arg in self.months:
                if not __validate(self.KW.MONTH, arg, cfg, [self.KW.KEYWORD]):
                    return cfg
            elif arg in self.keywords:
                if not __validate(self.KW.KEYWORD, arg, cfg, [self.KW.DAY, self.KW.MONTH]):
                    return cfg
            else:
                mapped_month = self._identify_month(arg)
                if mapped_month and not __validate(self.KW.MONTH, mapped_month, cfg):
                    return cfg
        return cfg

    # used to further parse given configuration and validate user arguments
    def _parse_config(self, config):
        api_cfg = {self.KW.EVENT: None, self.KW.MONTH: None,
                   self.KW.DAY: None, self.KW.KEYWORD: None, self.KW.ERROR: None}

        # check for events
        api_cfg[self.KW.EVENT] = config[self.KW.EVENT]
        if not api_cfg[self.KW.EVENT]:
            api_cfg[self.KW.EVENT] = random.choice(self.events)

        # track if we got date from keywords
        api_cfg[self.KW.KEYWORD] = False
        # check for keywords
        if config[self.KW.KEYWORD]:  # if keywords present we already have date
            api_cfg[self.KW.KEYWORD] = True
            # today's date
            date = datetime.datetime.now()
            # timestamp of one day
            timestamp_day = datetime.timedelta(days=1)
            if config[self.KW.KEYWORD] == self.KW.DATE_YESTERDAY:
                # if keyword was yesterday substitue timestamp from date
                date -= timestamp_day
            elif config[self.KW.KEYWORD] == self.KW.DATE_TOMORROW:
                # if keyword was yesterday add timestamp to date
                date += timestamp_day

            api_cfg[self.KW.DAY] = date.day
            api_cfg[self.KW.MONTH] = date.month
        else:  # if keywords were not passed we need to find/randomize date
            # check for month
            api_cfg[self.KW.MONTH] = config[self.KW.MONTH]
            if not api_cfg[self.KW.MONTH]:
                api_cfg[self.KW.MONTH] = random.choice(self.months)

            # check for day
            api_cfg[self.KW.DAY] = config[self.KW.DAY]
            if not api_cfg[self.KW.DAY]:
                api_cfg[self.KW.DAY] = random.randint(1, 29)

        return api_cfg

    # generates query to be sent over web to given API
    def _generate_query(self, api_cfg):
        day = api_cfg[self.KW.DAY]

        if api_cfg[self.KW.KEYWORD]:
            # if keyword exists, then we are taking data from datetime an month is type of int
            month = api_cfg[self.KW.MONTH]
        else:
            # otherwise it's string
            month = self.months.index(api_cfg[self.KW.MONTH]) + 1

        # url = api.com/date/<month>/<day>
        query_str = '{}/{}/{}'.format(self.url, month, day)
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
            facts_arr = result['data'][api_cfg[self.KW.EVENT].capitalize()]
            fact = random.choice(facts_arr)
            # generate data from result
            data = {
                'date': result['date'],
                'type': api_cfg[self.KW.EVENT],
                'year': fact['year'],
                'text': fact['text'],
                'links': fact['links']
            }
            jarvis.spinner_stop()
        except BaseException:
            jarvis.spinner_stop(
                message="\nTask execution Failed!", color=Fore.RED)
            jarvis.say(
                "Please check that arguments are correct and day of month is valid!", Fore.RED)
            jarvis.say(
                "If error occures again, then API might have crashed. Try again later.\n", Fore.RED)
        finally:
            return data

    # prints result of query in a human readable way
    def _print_result(self, jarvis, result):
        # first line of output contains date of fact
        jarvis.say('\nDate : {} of {}'.format(
            result['date'], result['year']), Fore.BLUE)

        # second line contains information
        jarvis.say('{} : {}'.format(result['type'], result['text']), Fore.BLUE)

        # next lines will be links to external sources
        jarvis.say('External links : ', Fore.BLUE)
        result['links'] = result['links'][:self.MAX_LINK]
        for i in range(len(result['links'])):
            jarvis.say('    {}). {}'.format(
                i + 1, result['links'][i]['link']), Fore.BLUE)
