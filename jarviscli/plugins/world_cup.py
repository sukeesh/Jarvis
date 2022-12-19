from plugin import plugin
from colorama import Fore


data = {1930:'Uruguay',
        1934:'Italy',
        1938:'Italy',
        1950:'Uruguay',
        1954:'Germany',
        1958:'Brazil',
        1962:'Brazil',
        1966:'England',
        1970:'Brazil',
        1974:'Germany',
        1978:'Argentina',
        1982:'Italy',
        1986:'Argentina',
        1990:'Germany',
        1994:'Brazil',
        1998:'France',
        2002:'Brazil',
        2006:'Germany',
        2010:'Spain',
        2014:'Germany',
        2018:'France',
        2022:'Argentina'}


@plugin("world_cup")
def hello_world(jarvis,s):
    if not s or 'help' in s:
        jarvis.say("world_cup year: returns the champion of that year",Fore.GREEN)
        jarvis.say("world_cup country: returns the number of titles of country",Fore.GREEN)
    else:
        args = s.split()
        if len(args) > 1:
            jarvis.say("world_cup year: returns the champion of that year",Fore.GREEN)
            jarvis.say("world_cup country: returns the number of titles of country",Fore.GREEN)
        else:

            if args[0].isnumeric():
                year = int(args[0])
                country = data.get(year,'There were no World Cup on this year!')
                jarvis.say(country)
            else:
                country = args[0]
                country = country.lower()
                count = 0

                for value in data.values():
                    if value.lower() == country:
                        count += 1
                
                jarvis.say(f"{count} titles")
                