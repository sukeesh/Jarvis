from plugin import plugin
import csv

@plugin("write_agenda")
def agenda(jarvis, s):
    exit = False
    csv_columns = ['Title','Description']
    mydict = {}

    while(exit==False):
        event_title = input("Write down the event title: ")
        event_description = input("Write down the event description: ")
        event_option = input("Anything more?(y/n): ")
        mydict[event_title] = event_description

        if(event_option =='n'):
            exit=True

    if bool(mydict):
        print('New inputs are: ' + str(mydict))
        try:
            with open('agenda.csv','w') as csv_file:
                writer = csv.writer(csv_file)
                for key, value in mydict.items():
                    writer.writerow([key, value])
        except IOError:
            print("I/O error") 
    else:
        print('Nothing for the agenda')