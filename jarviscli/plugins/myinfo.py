from plugin import plugin
import csv


@plugin("myinfo")
def myinfo(jarvis, s):
    # Save personal information about the user for future configuration

    mydict = {}
    name_parameter = input("Write down your name: ")
    born_date = input("Write down your born date(YYYY/MM/DD): ")
    city_parameter = input("Write down your city's name: ")

    mydict['name_parameter'] = name_parameter
    mydict['born_date'] = born_date
    mydict['city_parameter'] = city_parameter

    if bool(mydict):
        print('New inputs are: ' + str(mydict))
        try:
            with open('myinfo.csv', 'w') as csv_file:
                writer = csv.writer(csv_file)
                for key, value in mydict.items():
                    writer.writerow([key, value])
        except IOError:
            print("I/O error")
    else:
        print('Nothing in myinfo')
