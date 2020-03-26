from plugin import plugin, require

@require(network=True)
@plugin('history')
class history:
    """
    Provides you with a random hisotry fact

    Enter 'history' to use:
    * history <event> <day> <month>
    """

    def __init__(self):
        self.url = "http://history.muffinlabs.com/date/{}/{}" # .format(month, day)
        self.events = {'birth', 'death', 'events'}
        self.months = {'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'}

    def __call__(self, jarvis, s):
        config = self._parse_arguments(s)
        print(config)
        
    def _parse_arguments(self, args):
        split_args = args.split()
        cfg = {}
        for arg in split_args:
            if arg in self.events:
                cfg['event'] = arg
            elif arg  in self.months:
                cfg['month'] = arg
            elif arg.isdigit():
                cfg['day']  = arg
        return cfg
