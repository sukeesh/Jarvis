from colorama import Fore
from pycricbuzz import Cricbuzz
import six

c = Cricbuzz()


def match_id(desc):
    all_matches = c.matches()
    for match in all_matches:
        if match['mchdesc'].title() == desc:
            return match['id']
    else:
        return None


def all_matches():
    match_data = c.matches()
    matches = []
    for match in match_data:
        matches.append(match['mchdesc'])
    return matches


def live_score(desc):
    mid = match_id(desc)
    res = c.matches()
    for value in res:
        if value['id'] == mid:
            if value['mchstate'] == 'preview':
                text = Fore.RED + "MATCH YET TO BEGIN"
                return text
    data = c.livescore(mid)
    score = {}
    score['matchinfo'] = "{}, {}".format(data['matchinfo']['mnum'], data['matchinfo']['mchdesc'])
    score['status'] = "{}, {}".format(data['matchinfo']['mchstate'].title(), data['matchinfo']['status'])
    score['bowling'] = data['bowling']
    score['batting'] = data['batting']

    text = ''
    text += Fore.LIGHTYELLOW_EX + score['matchinfo'] + '\n' + score['status'] + '\n\n'
    text += Fore.BLUE + score['batting']['team'] + '\n' + Fore.BLACK

    for scr in reversed(score['batting']['score']):
        text += "{} :- {}/{} in {} overs\n".format(scr['desc'], scr['runs'], scr['wickets'], scr['overs'])
    for b in reversed(score['batting']['batsman']):
        text += "{} : {}({}) \n".format(b['name'].strip('*'), b['runs'], b['balls'])
    text += Fore.BLUE + "\n" + score['bowling']['team'] + '\n' + Fore.BLACK
    for scr in reversed(score['bowling']['score']):
        text += "{} :- {}/{} in {} overs\n".format(scr['desc'], scr['runs'], scr['wickets'], scr['overs'])
    for b in reversed(score['bowling']['bowler']):
        text += "{} : {}/{} \n".format(b['name'].strip('*'), b['wickets'], b['runs'])
    text += Fore.RESET
    return text


def commentary(desc):
    mid = match_id(desc)
    data = c.commentary(mid)
    comm = {}
    comm['matchinfo'] = "{}, {}".format(data['matchinfo']['mnum'], data['matchinfo']['mchdesc'])
    comm['status'] = "{}, {}".format(data['matchinfo']['mchstate'].title(), data['matchinfo']['status'])
    comm['commentary'] = data['commentary']
    text = ''
    text += Fore.LIGHTYELLOW_EX + comm['matchinfo'] + '\n' + comm['status'] + '\n\n' + Fore.RESET
    for com in comm['commentary']:
        text += "{}\n\n".format(com)

    return text


def scorecard(desc):
    mid = match_id(desc)
    data = c.scorecard(mid)
    card = {}
    card['matchinfo'] = "{}, {}".format(data['matchinfo']['mnum'], data['matchinfo']['mchdesc'])
    card['status'] = "{}, {}".format(data['matchinfo']['mchstate'].title(), data['matchinfo']['status'])
    card['scorecard'] = data['scorecard']
    text = ''
    text += Fore.LIGHTYELLOW_EX + card['matchinfo'] + '\n' + card['status'] + '\n\n'
    text += Fore.BLACK + '*' * 35 + '\n\n'

    for scr in reversed(card['scorecard']):
        text += Fore.LIGHTYELLOW_EX + "{} {}\n{}/{} in {} overs\n\n".format(scr['batteam'], scr['inngdesc'], scr['runs'], scr['wickets'],
                                                                            scr['overs'])
        text += Fore.BLUE + "Batting\n"
        text += Fore.RED + "{:<17} {:<3} {:<3} {:<3} {}\n\n".format('Name', 'R', 'B', '4', '6')
        for b in scr['batcard']:
            text += Fore.BLACK + "{:<17} {:<3} {:<3} {:<3} {}\n{}\n\n".format(b['name'], b['runs'], b['balls'], b['fours'], b['six'],
                                                                              b['dismissal'])
        text += Fore.LIGHTYELLOW_EX + "-" * 35 + "\n\n"
        text += Fore.BLUE + "Bowling\n"
        text += Fore.RED + "{:<17} {:<5} {:<3} {:<3} {}\n\n".format('Name', 'O', 'M', 'R', 'W')
        for b in scr['bowlcard']:
            text += Fore.BLACK + "{:<17} {:<5} {:<3} {:<3} {}\n\n".format(b['name'], b['overs'], b['maidens'], b['runs'],
                                                                          b['wickets'])
        text += Fore.BLUE + '*' * 35 + '\n\n'
    return text


def score(self):
    matches = all_matches()
    print(Fore.RED + "\nALL MATCHES\n" + Fore.LIGHTBLUE_EX)
    for i, m in enumerate(matches, 1):
        print("{}. {}".format(str(i), m))
    if six.PY2:
        choice = int(raw_input(Fore.RED + '\nEnter choice (number): ' + Fore.RESET))
    else:
        choice = int(input(Fore.RED + '\nEnter choice (number): ' + Fore.RESET))
    while choice < 1 or choice > len(matches):
        print(Fore.BLACK + '\nWrong choice')
        if six.PY2:
            choice = int(raw_input(Fore.RED + '\nEnter choice again: ' + Fore.RESET))
        else:
            choice = int(input(Fore.RED + '\nEnter choice again: ' + Fore.RESET))

    desc = matches[choice - 1].title()
    print('')
    res = live_score(desc)
    print(res)
    print("\n")
    if(res == Fore.RED + "MATCH YET TO BEGIN"):
        return
    print(live_score(desc))
    print(Fore.LIGHTBLUE_EX + '1. Full Score Card')
    print('2. Commentary')
    print('3. Refresh Score')
    print('4. Quit' + Fore.RESET)

    if six.PY2:
        choice = int(raw_input(Fore.RED + '\nEnter choice (number): ' + Fore.RESET))
    else:
        choice = int(input(Fore.RED + '\nEnter choice (number): ' + Fore.RESET))
    while choice < 1 or choice > 4:
        print(Fore.BLACK + '\nWrong choice')
        if six.PY2:
            choice = int(raw_input(Fore.RED + '\nEnter choice again: ' + Fore.RESET))
        else:
            choice = int(input(Fore.RED + '\nEnter choice again: ' + Fore.RESET))
    print('')

    if choice == 1:
        ref = 'y'
        while ref == 'y':
            print(scorecard(desc))
            if six.PY2:
                ref = raw_input(Fore.RED + 'Do you want to refresh:(y/n) ' + Fore.RESET)
            else:
                ref = input(Fore.RED + 'Do you want to refresh:(y/n) ' + Fore.RESET)
            print('\n')

    elif choice == 2:
        ref = 'y'
        while ref == 'y':
            print(commentary(desc))
            if six.PY2:
                ref = raw_input(Fore.RED + 'Do you want to refresh:(y/n) ' + Fore.RESET)
            else:
                ref = input(Fore.RED + 'Do you want to refresh:(y/n) ' + Fore.RESET)
            print('\n')

    elif choice == 3:
        ref = 'y'
        while ref == 'y':
            print(live_score(desc))
            if six.PY2:
                ref = raw_input(Fore.RED + 'Do you want to refresh:(y/n) ' + Fore.RESET)
            else:
                ref = input(Fore.RED + 'Do you want to refresh:(y/n) ' + Fore.RESET)
            print('\n')
