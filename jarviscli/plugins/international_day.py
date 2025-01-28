import csv
import datetime
from colorama import Fore
from plugin import plugin


@plugin("international day")
class InternationalDay:
    """
    Jarvis plugin that prints the
    International Day of the current date or of the
    input date the user enters.
    """
    def __call__(self, jarvis, s):
        """
        Calls the needed methods to execute the plugin.
        """
        jarvis.say("\nWhich date would you like to know"
                   " there is an international day for? ")
        # Formats the printed message
        message = Fore.RESET + Fore.YELLOW + \
            "[1]" + Fore.RESET + " For today's!\n"
        message += Fore.RESET + Fore.YELLOW + "[2]" + Fore.RESET + \
            " For another day...\n"
        jarvis.say(message)
        # Takes the user's input choice.
        choice = jarvis.input("Please enter your choice: ")
        # Loop to validate the input choice.
        while True:
            try:
                # Find International Day for the current date.
                if choice == "1":
                    current_date = self.find_date()
                    current_day, current_month = self.split_date(current_date)
                    # Open the csv file that contains the International Days
                    # which is located in the data folder.
                    with open(r'jarviscli\data\international_days.csv')\
                            as csv_file:
                        print_message = \
                            self.find_international_day(current_date,
                                                        current_day,
                                                        current_month,
                                                        csv_file)
                        print(print_message)
                    break
                # Find International Day for the given date.
                elif choice == "2":
                    # Takes the user's input date.
                    another_date = jarvis.input("\nPlease enter the date"
                                                " you like"
                                                " (ex. 2021-09-21): ")
                    # Validates the input date to be in the proper format.
                    while not self.validate_input_date(another_date):
                        jarvis.say("Please enter a valid date! ",
                                   Fore.YELLOW)
                        another_date = jarvis.input()
                    # Spits the input date into month and day variables.
                    # ex. 2021-09-21 --> month = 09, day = 21
                    month = another_date.split('-')[1]
                    day = another_date.split('-')[2]
                    with open(r'jarviscli\data\international_days.csv')\
                            as csv_file:
                        print_message = self.find_international_day(
                            another_date, int(day), int(month), csv_file)
                        print(print_message)
                    break
                else:
                    raise ValueError
            except ValueError:
                jarvis.say("Oops! That was no valid choice. Try again...",
                           Fore.YELLOW)
                choice = jarvis.input()

    def validate_input_date(self, input_date):
        """
        Function that validates the date to fit the proper format.
        """
        try:
            datetime.datetime.strptime(input_date, '%Y-%m-%d')
        except ValueError:
            return False
        return True

    def find_international_day(self, current_date, current_day,
                               current_month, csv_file):
        """
        Function that searches for the International Day of
        the given date in the csv file.
        """
        csv_reader = csv.reader(csv_file, delimiter=';')
        print_message = "The concerned date is "
        for row in csv_reader:
            # row[0] column stores the days of the month.
            if row[0] == str(current_day):
                # Checks if the string in the row is empty.
                # If not it includes the International Day
                if not row[current_month]:
                    print_message += Fore.YELLOW +\
                        str(current_date) + Fore.RESET + \
                        ", but there isn't an International" \
                        " Day for today :("
                    break
                else:
                    print_message += Fore.RESET + Fore.YELLOW + \
                        str(current_date) + \
                        Fore.RESET + ", " + \
                        str(row[current_month])
                    break
        return print_message

    def split_date(self, current_date):
        """
        Function that returns the day and month
        of the current date.
        """
        current_day = current_date.day
        current_month = current_date.month
        return current_day, current_month

    def find_date(self):
        """
        Function that returns the current date
        from the computer using the datetime
        library
        """
        current_datetime = datetime.datetime.now()
        current_date = current_datetime.date()
        return current_date
