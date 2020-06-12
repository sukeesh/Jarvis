import logging
from random import randint
import smtplib
import re
import random
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

def spinit(list):
    return(random.choice(list))

@ask.intent("AnswerIntent")
def answer(ans):

    if ans == "Spin the Wheel" :
        def next_round():
            round_msg = render_template('enter')
            return question(round_msg)

        @ask.intent("STWAnswerIntent", convert={'first': int, 'second': int, 'third': int, 'fourth': int, 'fifth': int, 'sixth': int, 'seventh': int, 'eighth': int, 'nineth': int, 'tenth': int})
        def answer(first, second, third, fourth, fifth, sixth, seventh, eighth, nineth, tenth):
            wheel = []
            wheel.append(first)
            wheel.append(second)
            wheel.append(third)
            wheel.append(fourth)
            wheel.append(fifth)
            wheel.append(sixth)
            wheel.append(seventh)
            wheel.append(eighth)
            wheel.append(nineth)
            wheel.append(tenth)
            res = spinit(wheel)
            msg = render_template('result')
            return statement(msg)

@ask.launch
def new_game():
    welcome_msg = render_template('welcome_jarvis')
    return question(welcome_msg)
            
if __name__ == '__main__':
    app.run(debug=True)
