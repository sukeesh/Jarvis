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

def exercise_level(self, level):
    multipliers = {1: 1.2, 2: 1.4, 3: 1.6, 4: 1.95}
    multiplier = multipliers.get(level, 1)
    return multiplier

@ask.launch
def new_game():
    welcome_msg = render_template('welcome_jarvis')
    return question(welcome_msg)

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
        
    elif ans == "Calories" :
        def enter_cal():
            ent_msg = render_template('enter_cal')
            return statement(ent_msg)

        @ask.intent("CaloriesAnswerIntent", convert={'age': int, 'height': int, 'weight': float, 'level': int})
        def answer(age, height, weight, level, gender):
            gender_no = 0
            if gender == "male" or gender == "man" or gender == "m" :
                gender_no = 5
            elif gender == "female" or gender == 'woman' or gender == "f" :
                gender_no = -161
            brm = float(10 * weight + 6.25 * height - 5
                * age + gender_no) * self.exercise_level(level)
            brm_loss = brm - 500.0
            brm_put_on = brm + 500.0
            dci = str(brm)
            lwc = str(brm_loss)
            powc = str(brm_put_on)
            msg = render_template('cal_result')
            return statement(msg)
        
    elif ans == "Temperature Converter" :
        def enter_temp():
            ent_msg = render_template('enter_temp_type')
            return statement(ent_msg)

        @ask.intent("TempConvAnswerIntent", convert={'temp': float})
        def answer(temp, type):
            if type == "Celsius" :
                new_temp = round((temp * 9 / 5 + 32), 2)
                new_type == "Fahrenheit"
            elif type == "Fahrenheit" :
                new_temp = round(((temp - 32) * 5 / 9), 2)
                new_type = "Celsius"
            msg = render_template('tempconv_result')
            return statement(msg)
            
if __name__ == '__main__':
    app.run(debug=True)
