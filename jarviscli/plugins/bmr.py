from plugin import plugin


@plugin("bmr")
def bmr(jarvis, s):
    """Prints \"hello world!\""""

    # gets inputs
    jarvis.say("M or F")
    sex = jarvis.input()
    jarvis.say("What is your height (cm) ?")
    height = jarvis.input()
    jarvis.say("What is your weight (kg) ?")
    weight = jarvis.input()
    jarvis.say("What is your age ?")
    age = jarvis.input()

    # for catching errors
    try:
        # formula changes based on sex
        if(sex == 'F'):
            Bmr = (float(height) * 6.25) + (float(weight) * 9.99) - (float(age) * 4.92) - 116
            jarvis.say(str(Bmr))
        elif(sex == 'M'):
            Bmr = (float(height) * 6.25) + (float(weight) * 9.99) - (float(age) * 4.92) - 5
            jarvis.say(str(Bmr))
        else:
            jarvis.say("try again! please follow the format")
    except BaseException:
        jarvis.say("try again! please follow the format")
