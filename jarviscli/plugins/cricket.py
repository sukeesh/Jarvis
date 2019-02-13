from colorama import Fore
from pycricbuzz import Cricbuzz
from plugin import plugin, require
from plugins.animations import SpinnerThread


@require(network=True)
@plugin('cricket')
class Cricket():
    """
    Enter cricket and follow the instructions
    """

    def __init__(self):
        self.c = Cricbuzz()

    def __call__(self, jarvis, s):
        self._refresh(jarvis)
        self.score(jarvis)

    def _refresh(self, jarvis):
        spinner = SpinnerThread('Fetching ', 0.15)
        spinner.start()
        self.all_match_data = self.c.matches()
        self.matches = []
        d = {}
        for match in self.all_match_data:
            d['id'] = match['id']
            d['srs'] = match['srs']
            d['mnum'] = match['mnum']
            self.matches.append(d.copy())
        spinner.stop()
        jarvis.say('DONE fetching match details', Fore.GREEN)

    def live_score(self, index):
        if self.all_match_data[index]['mchstate'] == 'preview':
            return(Fore.RED + "MATCH YET TO BEGIN")
        selected_match = self.all_match_data[index]
        data = self.c.livescore(self.matches[index]['id'])
        score = {}
        score['matchinfo'] = "{}, {}".format(
            selected_match['srs'], selected_match['mnum'])
        score['status'] = "{}".format(selected_match['status'])
        score['bowling'] = data['bowling']
        score['batting'] = data['batting']

        text = ''
        text += Fore.LIGHTYELLOW_EX + \
            score['matchinfo'] + '\n' + score['status'] + '\n\n'

        text += Fore.BLUE + score['batting']['team'] + Fore.BLACK
        for scr in reversed(score['batting']['score']):
            text += " :- {}/{} in {} overs\n".format(
                scr['runs'], scr['wickets'], scr['overs'])
        for b in reversed(score['batting']['batsman']):
            text += "{} : {}({}) \n".format(
                b['name'].strip('*'), b['runs'], b['balls'])

        text += Fore.BLUE + '\n' + score['bowling']['team'] + Fore.BLACK
        for scr in reversed(score['bowling']['score']):
            text += " :- {}/{} in {} overs\n".format(
                scr['runs'], scr['wickets'], scr['overs'])
        for b in reversed(score['bowling']['bowler']):
            text += "{} : {}/{} \n".format(b['name'].strip('*'),
                                           b['wickets'], b['runs'])
        text += Fore.RESET

        return text

    def commentary(self, index):
        selected_match = self.all_match_data[index]
        data = self.c.commentary(self.matches[index]['id'])
        comm = {}
        comm['matchinfo'] = "{}, {}".format(
            selected_match['srs'], selected_match['mnum'])
        comm['status'] = "{}".format(selected_match['status'])
        comm['commentary'] = data['commentary']
        text = []
        for com in comm['commentary']:
            line = ''
            if com['over']:
                line += com['over'] + ' : '
            line += "{}\n\n".format(com['comm'])
            # doing bold breaklines and italics looks good in terminal
            text.append(
                line.replace(
                    '<b>',
                    '\033[1m').replace(
                    '</b>',
                    '\033[0m') .replace(
                    '<br/>',
                    '\n').replace(
                    '<i>',
                    '\x1B[3m').replace(
                        '</i>',
                    '\x1B[23m'))

        text.reverse()

        commentary = Fore.LIGHTYELLOW_EX + \
            comm['matchinfo'] + '\n' + comm['status'] + '\n\n' + Fore.RESET
        for line in text:
            commentary += line

        return commentary

    def scorecard(self, index):
        selected_match = self.all_match_data[index]
        data = self.c.scorecard(self.matches[index]['id'])
        card = {}
        card['matchinfo'] = "{}, {}".format(
            selected_match['srs'], selected_match['mnum'])
        card['status'] = "{}".format(selected_match['status'])
        card['scorecard'] = data['scorecard']
        text = ''
        text += Fore.LIGHTYELLOW_EX + \
            card['matchinfo'] + '\n' + card['status'] + '\n\n'
        text += Fore.BLACK + '*' * 35 + '\n\n'

        for scr in reversed(card['scorecard']):
            text += Fore.LIGHTYELLOW_EX + "{}\nInnings: {}\n{}/{} in {} overs\n\n".format(
                scr['batteam'], scr['inng_num'], scr['runs'], scr['wickets'], scr['overs'])
            text += Fore.BLUE + "Batting\n"
            text += Fore.RED + \
                "{:<17} {:<3} {:<3} {:<3} {}\n\n".format('Name', 'R', 'B', '4', '6')
            for b in scr['batcard']:
                text += Fore.BLACK + "{:<17} {:<3} {:<3} {:<3} {}\n{}\n\n".format(
                    b['name'], b['runs'], b['balls'], b['fours'], b['six'], b['dismissal'])
            text += Fore.LIGHTYELLOW_EX + "-" * 35 + "\n\n"
            text += Fore.BLUE + "Bowling\n"
            text += Fore.RED + \
                "{:<17} {:<5} {:<3} {:<3} {}\n\n".format('Name', 'O', 'M', 'R', 'W')
            for b in scr['bowlcard']:
                text += Fore.BLACK + "{:<17} {:<5} {:<3} {:<3} {}\n\n".format(
                    b['name'], b['overs'], b['maidens'], b['runs'], b['wickets'])
            text += Fore.BLUE + '*' * 35 + '\n\n'
        return text

    def score(self, jarvis):
        print(Fore.RED + "\nALL MATCHES\n" + Fore.LIGHTBLUE_EX)
        if self.matches == []:
            print("No Matches Being Played!\n", Fore.RED)
            return
        for i, m in enumerate(self.matches, 1):
            print("{}. {} {}".format(str(i), m['srs'], m['mnum']))
        while True:
            try:
                choice = int(jarvis.input('\nEnter choice (number): ', Fore.RED))
                while choice < 1 or choice > len(self.matches):
                    print(Fore.BLACK + '\nWrong choice')
                    choice = int(jarvis.input('\nEnter choice again: ', Fore.RED))
                break
            except ValueError:
                print("Invalid type of choice. Please enter an integer number")

        selected_match_id = choice - 1
        print('')
        res = self.live_score(selected_match_id)
        print(res)

        if(res == Fore.RED + "MATCH YET TO BEGIN"):
            return

        while True:
            print(Fore.LIGHTBLUE_EX + '1. Full Score Card')
            print('2. Commentary')
            print('3. Refresh Score')
            print('4. Quit' + Fore.RESET)

            while True:
                try:
                    choice = int(jarvis.input('\nEnter choice (number): ', Fore.RED))
                    while choice < 1 or choice > 4:
                        print(Fore.BLACK + '\nWrong choice')
                        choice = int(jarvis.input('\nEnter choice again: ', Fore.RED))
                    break
                except ValueError:
                    print("Invalid type of choice. Please enter an integer number")
            print('')

            if choice == 1:
                print(self.scorecard(selected_match_id))
                ref = jarvis.input('Do you want to refresh:(y/n) ', Fore.RED)
                while ref == 'y':
                    print(self.scorecard(selected_match_id))
                    ref = jarvis.input('Do you want to refresh:(y/n) ', Fore.RED)

            elif choice == 2:
                print(self.commentary(selected_match_id))
                ref = jarvis.input('Do you want to refresh:(y/n) ', Fore.RED)
                while ref == 'y':
                    print(self.commentary(selected_match_id))
                    ref = jarvis.input('Do you want to refresh:(y/n) ', Fore.RED)

            elif choice == 3:
                ref = 'y'
                while ref == 'y':
                    print(self.live_score(selected_match_id))
                    ref = jarvis.input('Do you want to refresh:(y/n) ', Fore.RED)

            else:
                return
