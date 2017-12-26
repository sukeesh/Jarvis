import getpass
import os
from time import sleep
from selenium import webdriver
import six


def get_details():
    file = 'password.txt'

    # retrive password if saved previously

    if os.path.isfile(file):
        with open(file, 'r') as f:
            usr = f.readline()
            pwd = f.readline()
            usr = usr.strip('\n')

    # passwords are not saved

    else:
        if six.PY2:
            usr = raw_input('Enter Email Id: ')
        else:
            usr = input('Enter Email Id: ')
        pwd = getpass.getpass('Enter Password: ')
        if six.PY2:
            choice = raw_input('Do you want to save the id and password (y/n): ')
        else:
            choice = input('Do you want to save the id and password (y/n): ')
        if choice == 'y' or choice == 'Y':
            with open(file, 'w') as f:
                f.write(usr)
                f.write('\n')
                f.write(pwd)
    return usr, pwd


def fb_login(self):
    usr, pwd = get_details()
    try:
        driver = webdriver.Chrome('/usr/bin/chromedriver')
    except:
        driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')
    driver.get('https://www.facebook.com/')

    user_id = driver.find_element_by_id('email')
    user_id.send_keys(usr)
    sleep(2)

    password = driver.find_element_by_id('pass')
    password.send_keys(pwd)
    sleep(2)

    submit = driver.find_element_by_id('loginbutton')
    submit.click()
    if six.PY2:
        raw_input('Enter anything to end the session: ')
    else:
        input('Enter anything to end the session: ')
    driver.quit()
