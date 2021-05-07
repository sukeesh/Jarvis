from plugin import plugin
import csv, os, time, datetime

@plugin("write agenda")
def write_agenda(jarvis, s):
    loop = True
    invalid_input = False
    invalid_time = True
    invalid_date = True
    # list of column names
    header = ['DATE', 'TIME', 'PLACE', 'TITLE',
                   'DESCRIPTION']
    events_list = []

    while True:
        try:
            with open('agenda.csv', 'a', newline='') as csv_file:
                break #if the file is not open exit the loop and continue
        except IOError:
            input("Agenda file is open! Please close the Excel file and press Enter to retry.")


    while(loop):
        if (invalid_input == False):
            invalid_date = True
            while(invalid_date):
                event_date = jarvis.input("Write down the event date (ex. 2021-09-21): ")
                try:
                    datetime.datetime.strptime(event_date, '%Y-%m-%d')
                    invalid_date = False
                except ValueError:
                    invalid_date = True
                    print("Please enter a valid date!")
            while (invalid_time):
                event_time = jarvis.input("Write down the event time (ex. 13:00): ")
                try:
                    time.strptime(event_time, '%H:%M')
                    invalid_time = False
                except ValueError:
                    invalid_time = True
                    print("Please enter a valid time!")
            event_place = jarvis.input("Write down the event place: ")
            event_title = jarvis.input("Write down the event title: ")
            event_description = jarvis.input("Write down the event description: ")
            current_values = [event_date, event_time, event_place, event_title, event_description]
            events_list.append(current_values)
        event_option = jarvis.input("Would you like to add anything more?(y/n): ")

        if(event_option == 'y'):
            invalid_input = False # In case invalid input was given before
            continue
        elif(event_option == 'n'):
            loop = False
        else:
            print("Sorry, invalid input was given! Please try again.")
            invalid_input = True


    if not events_list: # List is empty
        print('Nothing for the agenda')
    else:
        print('New inputs are: ' + str(events_list))
        try:
            with open('agenda.csv', 'a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                # check if size of file is 0
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
        f = open('agenda.csv', 'r')
        reader = csv.reader(f)
        for row in reader:
            print(row)
        f.close()
    except BaseException:
        print('There is not an agenda')