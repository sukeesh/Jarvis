"""

Jarvis plugin for keeping your own personal
events' agenda! Using this feature
one can store in a csv file all the needed details for
an event to remember.  More specifically, these details
are date, time, place, title and description of the
upcoming event.

"""
import csv
import os
import time
import datetime
from plugin import plugin


@plugin("write agenda")
def write_agenda(jarvis, s):
    loop = True
    # variables to check invalid inputs in while loop
    invalid_input = False
    invalid_time = True
    invalid_date = True
    # list of column names
    header = ['DATE', 'TIME', 'PLACE', 'TITLE', 'DESCRIPTION']
    # list with event's details
    events_list = []

    # warning message in case agenda file is already open before
    # actually implementing write agenda feature
    while True:
        try:
            with open('agenda.csv', 'a', newline=''):
                # if the file is not open exit the loop and continue
                break
        except IOError:
            input("Agenda file is open! "
                  "Please close the Excel file and press Enter to retry.")

    # passing new event's inputs
    while loop:
        if not invalid_input:
            # check for the date input to fit the proper format
            while invalid_date:
                event_date = jarvis.input("Write down the event date"
                                          " (ex. 2021-09-21): ")
                try:
                    datetime.datetime.strptime(event_date, '%Y-%m-%d')
                    invalid_date = False
                except ValueError:
                    invalid_date = True
                    print("Please enter a valid date!")
            # check for the time input to fit the proper format
            while invalid_time:
                event_time = jarvis.input("Write down the event time"
                                          " (ex. 13:00): ")
                try:
                    time.strptime(event_time, '%H:%M')
                    invalid_time = False
                except ValueError:
                    invalid_time = True
                    print("Please enter a valid time!")
            event_place = jarvis.input("Write down the event place: ")
            event_title = jarvis.input("Write down the event title: ")
            event_description = jarvis.input("Write down "
                                             "the event description: ")
            current_values = [event_date, event_time, event_place,
                              event_title, event_description]
            events_list.append(current_values)
        event_option = jarvis.input("Would you like "
                                    "to add anything more?(y/n): ")

        if event_option == 'y':
            # restart variable's values
            # in case invalid input was given before
            invalid_input = False
            invalid_date = True
            invalid_time = True
        elif event_option == 'n':
            loop = False
        else:
            print("Sorry, invalid input was given! Please try again.")
            invalid_input = True

    # check if List is empty
    if not events_list:
        print('Nothing for the agenda')
    else:
        print('New inputs are: ' + str(events_list))
        try:
            with open('agenda.csv', 'a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                # check if size of file is 0 in order to add header
                # only the very first time agenda file is created
                if os.stat('agenda.csv').st_size == 0:
                    writer.writerow(header)
                # write multiple rows
                writer.writerows(events_list)
                csv_file.close()
        except IOError:
            print("I/O error!")


@plugin("read agenda")
def read_agenda(jarvis, s):
    try:
        file = open('agenda.csv', 'r')
        reader = csv.reader(file)
        for row in reader:
            print(row)
        file.close()
    except BaseException:
        print('There is not an agenda')
