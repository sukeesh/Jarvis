from selenium import webdriver
from time import sleep
import getpass
import os
import pyperclip
import six


def get_driver():
    try:
        driver = webdriver.Chrome('/usr/bin/chromedriver')
    except:
        driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')
    driver.get('https://twitter.com/login')

    return driver


def get_details():
    file = 'twitter_password.txt'

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


def twitter_login(self):
    usr, pwd = get_details()
    driver = get_driver()
    username_box = driver.find_element_by_class_name("js-username-field")
    username_box.send_keys(usr)
    sleep(2)

    password_box = driver.find_element_by_class_name("js-password-field")
    password_box.send_keys(pwd)
    sleep(2)

    submit = driver.find_element_by_css_selector(
        "button.submit.EdgeButton.EdgeButton--primary.EdgeButtom--medium")
    submit.click()
    print("Twitter Logged In")
    return driver


def twitter_tweet(self):
    print("1. write tweet")
    print("2. copy from clipboard")

    if six.PY2:
        choice = raw_input('Enter choice:')
    else:
        choice = input('Enter choice:')

    if int(choice) == 1:
        if six.PY2:
            tweet = raw_input('Enter tweet here:')
        else:
            tweet = input('Enter tweet here:')
    else:
        tweet = pyperclip.paste()

    driver = twitter_login(self)
    post_box = driver.find_element_by_id('tweet-box-home-timeline')
    post_box.send_keys(tweet)
    submit = driver.find_element_by_css_selector(
        'button.tweet-action.EdgeButton.EdgeButton--primary.js-tweet-btn')
    submit.click()
    print("Posted")

    return driver


def twitter_end(self, driver):
    if six.PY2:
        raw_input('Enter anything to end session: ')
    else:
        input('Enter anything to end session: ')
    driver.quit()
