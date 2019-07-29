from plugin import plugin
import csv


@plugin("write agenda")
def write_agenda(jarvis, s):
    exit = True
    csv_columns = ['Title', 'Description']
    mydict = {}

    while(exit):
        event_title = jarvis.input("Write down the event title: ")
        event_description = jarvis.input("Write down the event description: ")
        event_option = jarvis.input("Anything more?(y/n): ")
        mydict[event_title] = event_description

        if(event_option == 'n'):
            exit = False

    if bool(mydict):
        print('New inputs are: ' + str(mydict))
        try:
            with open('agenda.csv', 'w') as csv_file:
                writer = csv.writer(csv_file)
                for key, value in mydict.items():
                    writer.writerow([key, value])
        except IOError:
            print("I/O error")
    else:
        print('Nothing for the agenda')


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
