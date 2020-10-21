import random

import bs4
import requests
from colorama import Fore

from plugin import alias, plugin, require


@alias('project euler')
@require(network=True)
@plugin('euler')
class Euler():
    """
    Gives acces to problems from https://www.projecteuler.net via jarvis
    Usage: type 'euler' or 'project euler' and select the desired menu item.
    """

    def __init__(self):
        self.project_url = 'https://www.projecteuler.net'

    def __call__(self, jarvis, s):

        self.jarvis = jarvis

        # We need the number of the last problem
        # (in order to set limits on user's input)
        self.last_problem_id = self.get_last_problem_id()

        self.jarvis.say('Welcome to the ProjectEuler plugin!', Fore.GREEN)
        self.jarvis.say('-----------------------------------', Fore.GREEN)
        self.jarvis.say('')
        self.jarvis.say('Please select an option below:')
        self.jarvis.say('1) Get the problem by number')
        self.jarvis.say('2) Get random problem')
        self.jarvis.say('3) Info')
        # Just do nothing
        self.jarvis.say('4) Exit')
        choice = self.jarvis.input_number('Your choice: ', rtype=int, rmin=1, rmax=4)

        if choice == 1:
            problem_number = self.jarvis.input_number('Please, enter the desired number: ',
                                                      rtype=int,
                                                      rmin=1,
                                                      rmax=self.last_problem_id)
            self.get_problem_by_number(problem_number)
        elif choice == 2:
            # Generate random number
            problem_number = random.randint(1, self.last_problem_id)
            self.get_problem_by_number(problem_number)
        elif choice == 3:
            self.show_info()

    def get_problem_by_number(self, number):

        # Form link depending on the task number and get the page via requests module
        url = self.project_url + '/problem=' + str(number)
        try:
            page = requests.get(url)
        except ConnectionError:
            self.jarvis.say("Can't get info from site, exit", Fore.RED)
            return

        # Use bs4 to parse the page
        soup = bs4.BeautifulSoup(page.content, 'html.parser')

        # We are only interested in the block with id 'content'
        content = soup.find('div', id='content')

        # Get the title of the problem and print it
        problem_header = content.find('h2').get_text()
        header_to_show = 'Problem ' + str(number) + '. ' + problem_header
        self.jarvis.say('')
        self.jarvis.say(header_to_show, Fore.GREEN)

        # Get problem text
        problem_div = content.find('div', class_='problem_content')
        dirty_text = problem_div.get_text()

        # FIXME !!!
        # Not obvious way to remove duplicate newlines
        # But I still don't get along with regular expressions :)
        # FIXME !!!
        dirty_text = dirty_text.splitlines()
        i = 0
        while i < len(dirty_text) - 1:
            if dirty_text[i] == '' and dirty_text[i] == dirty_text[i + 1]:
                del dirty_text[i]
            else:
                i += 1

        # Also add empty lines (if no) before and after the text for pretty output
        if dirty_text[0] != '':
            dirty_text.insert(0, '')
        if dirty_text[len(dirty_text) - 1] != '':
            dirty_text.insert(len(dirty_text), '')

        # Form string again
        sep = '\n'
        problem_text = sep.join(dirty_text)

        # Print the text
        self.jarvis.say(problem_text)

        self.jarvis.say("If it seems to you that text is not displayed correctly you can follow the link below.", Fore.GREEN)
        self.jarvis.say(url)

    def show_info(self):
        self.jarvis.say('')
        self.jarvis.say('Website: ' + self.project_url, Fore.GREEN)
        self.jarvis.say("")

        info_text = "Project Euler (named after Leonhard Euler) is a website dedicated to a series of computational "
        info_text += "problems intended to be solved with computer programs. "
        info_text += "The project attracts adults and students interested in mathematics and computer programming. "
        info_text += "Since its creation in 2001 by Colin Hughes, Project Euler has gained notability and popularity worldwide. "
        info_text += "It now includes " + str(self.last_problem_id) + \
            " problems. A new one is added once every one or two weeks. "
        info_text += "Problems are of varying difficulty, but each is solvable in less than a minute of CPU time using an efficient "
        info_text += "algorithm on a modestly powered computer. "

        self.jarvis.say(info_text)
        self.jarvis.say("")

    def get_last_problem_id(self):
        # We need the number of the last problem
        # (in order to set limits on user's input)
        # Use bs4 to parse the page with recent problems
        url = self.project_url + '/recent'
        page = requests.get(url)
        soup = bs4.BeautifulSoup(page.content, 'html.parser')

        # We need only the table with recent problems
        problem_table = soup.find('table', id='problems_table')

        # The id of last problem is in the second row of the table (first is the header)
        # So get the second element of ResultSet
        last_problem_row = problem_table.find_all('tr')[1]

        # The id is in the first column ('td' tag)
        last_problem_id = int(last_problem_row.find('td').get_text())

        return(last_problem_id)
