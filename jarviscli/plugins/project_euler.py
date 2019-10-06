from plugin import plugin, alias, require
from colorama import Fore
import requests
import random
from bs4 import BeautifulSoup


@require(network=True)
@plugin('euler')
class Euler():

    def __init__(self):
        self.project_url = 'https://www.projecteuler.net'

        # Should be updated regularly
        # Or write the code wich gets this data item from the site
        self.last_problem = 682

    def __call__(self, jarvis, s):

        self.jarvis = jarvis

        self.jarvis.say('Welcome to the ProjectEuler plugin!', Fore.GREEN)
        self.jarvis.say('-----------------------------------', Fore.GREEN)
        self.jarvis.say('')
        self.jarvis.say('Please select an option below:')
        self.jarvis.say('1) Get the problem by number')
        self.jarvis.say('2) Get random problem')
        choice = self.jarvis.input_number('Your choice: ', rtype=int)

        if choice == 1:
            problem_number = self.jarvis.input_number('Please, enter the desired number: ', rtype=int)
            self.get_problem_by_number(problem_number)
        elif choice == 2:
            # Generate random number
            problem_number = random.randint(1, self.last_problem)
            self.get_problem_by_number(problem_number)


    def get_problem_by_number(self, number):

        # Form link depending on the number of the task and get the page via requests module
        url = self.project_url + '/problem=' + str(number)
        page = requests.get(url)

        # Use bs4 to parse the page
        soup = BeautifulSoup(page.content, 'html.parser')

        # We are only interested in the block with id 'content'
        content = soup.find('div', id='content')

        # Get the title of the problem and print it
        problem_header = content.find('h2').get_text()
        header_to_show = 'Problem ' + str(number) + '. ' + problem_header
        self.jarvis.say('')
        self.jarvis.say(header_to_show, Fore.GREEN)


