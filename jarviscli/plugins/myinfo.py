from plugin import plugin
import csv


@plugin("myinfo")
def myinfo(jarvis, s):
    # Save personal information about the user for future configuration

    mydict = {}
    name_parameter = input("Write down your name: ")
    age_parameter = input("Write down your age: ")
    city_parameter = input("Write down your city's name: ")

    mydict['name_parameter'] = name_parameter
    mydict['age_parameter'] = age_parameter
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
