import time
from colorama import Fore

from nba_api.stats.endpoints import playercareerstats as pcs
from nba_api.stats.static import players, teams
from plugin import plugin, require


@require(network=True)
@plugin('nbastats')
class nbaStats():
    '''
    NBA Plugin for getting statistics for current and former NBA players.
    Uses built-in NBA API.

    '''
    # dictionary of former and current NBA team names and abbreviations
    teams = {
        'NJN': 'New Jersey Nets',
        'SEA': 'Seattle SuperSonics',
        'NOH': 'New Orleans Hornets',
        'VAN': 'Vancouver Grizzlies',
        'CHH': 'Charlotte Hornets',
        'MNL': 'Minneapolis Lakers',
        'PHW': 'Philadelphia Warriors',
        'CIN': 'Cincinnati Royals',
        'KCK': 'Kansas City Kings',
        'SDC': 'San Diego Clippers',
        'NOJ': 'New Orleans Jazz',
        'BUF': 'Buffalo Braves',
        'STL': 'St. Louis Hawks',
        'SYR': 'Syracuse Nationals',
        'CAP': 'Capital Bullets',
        'BLT': 'Baltimore Bullets',
        'SDR': 'San Diego Rockets',
        'CHZ': 'Chicago Zephyrs',
        'SFW': 'San Francisco Warriors',
        'ROC': 'Rochester Royals',
        'AND': 'Anderson Packers',
        'TCB': 'Tri-Cities Blackhawks',
        'FTW': 'Fort Wayne Pistons',
        'MIH': 'Milwaukee Hawks',
        'ATL': 'Atlanta Hawks',
        'BOS': 'Boston Celtics',
        'BKN': 'Brooklyn Nets',
        'CHA': 'Charlotte Hornets',
        'CHI': 'Chicago Bulls',
        'CLE': 'Cleveland Cavaliers',
        'DAL': 'Dallas Mavericks',
        'DEN': 'Denver Nuggets',
        'DET': 'Detroit Pistons',
        'GSW': 'Golden State Warriors',
        'HOU': 'Houston Rockets',
        'IND': 'Indiana Pacers',
        'LAC': 'Los Angeles Clippers',
        'LAL': 'Los Angeles Lakers',
        'MEM': 'Memphis Grizzlies',
        'MIA': 'Miami Heat',
        'MIL': 'Milwaukee Bucks',
        'MIN': 'Minnesota Timberwolves',
        'NOP': 'New Orleans Pelicans',
        'NYK': 'New York Knicks',
        'OKC': 'Oklahoma City Thunder',
        'ORL': 'Orlando Magic',
        'PHI': 'Philadelphia 76ers',
        'PHX': 'Phoenix Suns',
        'POR': 'Portland Trail Blazers',
        'SAC': 'Sacramento Kings',
        'SAS': 'San Antonio Spurs',
        'TOR': 'Toronto Raptors',
        'UTA': 'Utah Jazz',
        'WAS': 'Washington Wizards'
    }
    # main function

    def __call__(self, jarvis):
        # full player stat program
        while True:
            # asks user for an NBA player
            playerName = checkValidPlayer(jarvis)

            # gets player statistics
            id = players.find_players_by_full_name(playerName)[0]['id']
            player = pcs.PlayerCareerStats(player_id=id)
            stats = player.get_data_frames()[0]
            stats = stats[['SEASON_ID', 'TEAM_ABBREVIATION', 'GP', 'MIN',
                           'PTS', 'REB', 'AST', 'STL', 'BLK', 'FG_PCT', 'FG3_PCT', 'FT_PCT']]

            # asks user for which stat they want
            userStat = getUserStat(jarvis)

            # asks user for the season they want stats from
            season = checkValidSeason(stats)

            # gives user stat information
            if userStat == 'GP':
                statGamesPlayed(stats, season, teams, playerName, jarvis)
            elif userStat == 'MIN':
                statMinutes(stats, season, teams, playerName, jarvis)
            elif userStat == 'PTS':
                statPts(stats, season, teams, playerName, jarvis)
            elif userStat == 'REB':
                statReb(stats, season, teams, playerName, jarvis)
            elif userStat == 'AST':
                statAst(stats, season, teams, playerName, jarvis)
            elif userStat == 'STL':
                statStl(stats, season, teams, playerName, jarvis)
            elif userStat == 'BLK':
                statBlk(stats, season, teams, playerName, jarvis)
            elif userStat == 'FG_PCT':
                statFgPct(stats, season, teams, playerName, jarvis)
            elif userStat == 'FG3_PCT':
                statThreePct(stats, season, teams, playerName, jarvis)
            else:
                statFtPct(stats, season, teams, playerName, jarvis)

            # asking if user wants to get more stats
            while True:
                userRepeat = jarvis.input(
                    'Would you like to get more statistics? (y/n) ', Fore.GREEN)
                if userRepeat == 'y':
                    break
                elif userRepeat == 'n':
                    break
                else:
                    jarvis.say(
                        '\nPlease enter either \'y\' or \'n\'.', Fore.YELLOW)
            if userRepeat == 'n':
                jarvis.say('\nGoodbye!', Fore.BLUE)
                return

    # user input functions
    def getUserStat(self, jarvis):
        statOptions = ['GP', 'MIN', 'PTS', 'REB', 'AST',
                       'STL', 'BLK', 'FG_PCT', 'FG3_PCT', 'FT_PCT']

        while True:
            jarvis.say('You can ask for the following stats:', Fore.BLUE)
            print('Games Played: GP')
            print('Average Minutes Played: MIN')
            print('Average Points Per Game: PTS')
            print('Average Rebounds Per Game: REB')
            print('Average Assists Per Game: AST')
            print('Average Steals Per Game: STL')
            print('Average Blocks Per Game: BLK')
            print('Field Goal %: FG_PCT')
            print('Three Point %: FG3_PCT')
            print('Free Throw %: FT_PCT')

            # asks user for stat
            userStat = jarvis.input(
                'What statistic would you like? ', Fore.GREEN)
            userStat = userStat.upper()
            if userStat in statOptions:
                return userStat
            else:
                print()
                jarvis.say(
                    'Please type a valid statistic. (ex. PTS)', Fore.YELLOW)
                print()
                time.sleep(0.3)

    def checkValidPlayer(self, jarvis):
        playerNames = []
        for info in players.get_players():
            playerNames.append(info['full_name'])

        while True:
            playerName = jarvis.input(
                'Please enter an NBA Player\'s name (be sure to capitalize accurately): ', Fore.GREEN)
            if playerName in playerNames:
                break
            else:
                jarvis.say(
                    'Player not found! Please enter a valid NBA player. Make sure spelling and capitalization is correct!', Fore.GREEN)
                print()
                time.sleep(0.3)
        return playerName

    def checkValidSeason(self, stats, jarvis):
        seasonYears = []
        for years in stats['SEASON_ID']:
            seasonYears.append(years)

        jarvis.say(f'You can pick from the following years:', Fore.BLUE)
        for year in range(len(seasonYears)):
            print(f'{year + 1}) {seasonYears[year]}')

        while True:
            season = jarvis.input(
                'What year do you want stats from? (ex. 2022-23): ', Fore.GREEN)
            if season in seasonYears:
                break
            else:
                jarvis.say(
                    'Season not found! Please enter a valid season. (try checking formatting!)', Fore.YELLOW)
                print()
                time.sleep(0.3)
        return season

    def getSeasonRow(self, stats, season, jarvis):
        rowTeams = {}
        for i in stats['SEASON_ID']:
            if i == season:
                for j in range(len(stats['SEASON_ID'])):
                    if stats.iloc[j]['SEASON_ID'] == season:
                        rowTeams[j] = stats.iloc[j]['TEAM_ABBREVIATION']

        keyList = list(rowTeams.keys())
        valueList = list(rowTeams.values())

        if len(rowTeams) == 1:
            return keyList[0]

        jarvis.say(
            f'This player has played for more than one team during the {season} season.', Fore.BLUE)
        while True:
            jarvis.say('You can pick the following teams:', Fore.BLUE)
            for team in rowTeams:
                print(rowTeams.get(team))
            teamChoice = jarvis.input(
                'Pick a team (type TOT for total): ', Fore.GREEN)
            teamChoice = teamChoice.upper()
            if teamChoice in rowTeams.values():
                position = valueList.index(teamChoice)
                seasonRow = keyList[position]
                return seasonRow
            else:
                jarvis.say('Please enter a valid team.', Fore.YELLOW)
                print()
                time.sleep(0.3)

    def getTeam(stats, teams, row):
        teamAbb = stats.iloc[row]['TEAM_ABBREVIATION']
        teamName = teams.get(teamAbb)
        return teamName

    # stat functions
    def statGamesPlayed(self, stats, season, teams, playerName, jarvis):
        for i in stats:
            stats[i] = stats[i].fillna(0)
        seasonRow = getSeasonRow(stats, season)
        teamName = getTeam(stats, teams, seasonRow)
        gp = stats.iloc[seasonRow]['GP']
        jarvis.say(
            f'\nDuring the {season} season, {playerName} played {gp} games on the {teamName}.', Fore.CYAN)

    def statMinutes(self, stats, season, teams, playerName, jarvis):
        for i in stats:
            stats[i] = stats[i].fillna(0)
        seasonRow = getSeasonRow(stats, season)
        teamName = getTeam(stats, teams, seasonRow)
        min = stats.iloc[seasonRow]['MIN'] / stats.iloc[seasonRow]['GP']
        jarvis.say(
            f'\nDuring the {season} season, {playerName} averaged {min:.1f} minutes on the {teamName}.', Fore.CYAN)

    def statPts(self, stats, season, teams, playerName, jarvis):
        seasonRow = getSeasonRow(stats, season)
        for i in stats:
            stats[i] = stats[i].fillna(0)
        avg = stats.iloc[seasonRow]['PTS'] / stats.iloc[seasonRow]['GP']
        teamName = getTeam(stats, teams, seasonRow)
        jarvis.say(
            f'\nWhile playing for the {teamName} during the {season} season, {playerName} averaged {avg:.1f} points per game.', Fore.CYAN)

    def statReb(self, stats, season, teams, playerName, jarvis):
        seasonRow = getSeasonRow(stats, season)
        for i in stats:
            stats[i] = stats[i].fillna(0)
        avg = stats.iloc[seasonRow]['REB'] / stats.iloc[seasonRow]['GP']
        teamName = getTeam(stats, teams, seasonRow)
        jarvis.say(
            f'\nWhile playing for the {teamName} during the {season} season, {playerName} averaged {avg:.1f} rebounds per game.', Fore.CYAN)

    def statAst(self, stats, season, teams, playerName, jarvis):
        seasonRow = getSeasonRow(stats, season)
        for i in stats:
            stats[i] = stats[i].fillna(0)
        avg = stats.iloc[seasonRow]['AST'] / stats.iloc[seasonRow]['GP']
        teamName = getTeam(stats, teams, seasonRow)
        jarvis.say(
            f'\nWhile playing for the {teamName} during the {season} season, {playerName} averaged {avg:.1f} assists per game.', Fore.CYAN)

    def statStl(self, stats, season, teams, playerName, jarvis):
        seasonRow = getSeasonRow(stats, season)
        for i in stats:
            stats[i] = stats[i].fillna(0)
        avg = stats.iloc[seasonRow]['STL'] / stats.iloc[seasonRow]['GP']
        teamName = getTeam(stats, teams, seasonRow)
        jarvis.say(
            f'\nWhile playing for the {teamName} during the {season} season, {playerName} averaged {avg:.1f} steals per game.', Fore.CYAN)

    def statBlk(self, stats, season, teams, playerName, jarvis):
        seasonRow = getSeasonRow(stats, season)
        for i in stats:
            stats[i] = stats[i].fillna(0)
        avg = stats.iloc[seasonRow]['BLK'] / stats.iloc[seasonRow]['GP']
        teamName = getTeam(stats, teams, seasonRow)
        jarvis.say(
            f'\nWhile playing for the {teamName} during the {season} season, {playerName} averaged {avg:.1f} blocks per game.', Fore.CYAN)

    def statFgPct(self, stats, season, teams, playerName, jarvis):
        seasonRow = getSeasonRow(stats, season)
        for i in stats:
            stats[i] = stats[i].fillna(0)
        avg = stats.iloc[seasonRow]['FG_PCT'] / stats.iloc[seasonRow]['GP']
        teamName = getTeam(stats, teams, seasonRow)
        jarvis.say(
            f'\nDuring the {season} season, {playerName} had a {avg:.1f}% field goal percentage while playing for the {teamName}.', Fore.CYAN)

    def statThreePct(self, stats, season, teams, playerName, jarvis):
        seasonRow = getSeasonRow(stats, season)
        for i in stats:
            stats[i] = stats[i].fillna(0)
        avg = stats.iloc[seasonRow]['FG3_PCT'] / stats.iloc[seasonRow]['GP']
        teamName = getTeam(stats, teams, seasonRow)
        jarvis.say(
            f'\nDuring the {season} season, {playerName} had a {avg:.1f}% three-point percentage while playing for the {teamName}.', Fore.CYAN)

    def statFtPct(self, stats, season, teams, playerName, jarvis):
        seasonRow = getSeasonRow(stats, season)
        for i in stats:
            stats[i] = stats[i].fillna(0)
        avg = stats.iloc[seasonRow]['FT_PCT'] / stats.iloc[seasonRow]['GP']
        teamName = getTeam(stats, teams, seasonRow)
        jarvis.say(
            f'\nDuring the {season} season, {playerName} had a {avg:.1f}% free throw percentage while playing for the {teamName}.', Fore.CYAN)
