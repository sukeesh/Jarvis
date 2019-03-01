from plugin import plugin


@plugin("health bmi")
def health_bmi(jarvis, s):
    """
    Tells the Body Mass Index(BMI).
    It is a measure of body mass based on height and weight.
    Add metric height(cm) and weight(kg). No decimal weight for now.
    #Example: health bmi 182 86
    ^Source: https://en.wikipedia.org/wiki/Body_mass_index
    """

    strings = s.split()
    if(len(strings) == 2):
        height = float(strings[0]) * float(strings[0])
        weight = float(strings[1])
    else:
        jarvis.say("Please add height(m) and weight(kg)!")
        return None

    if(height > 0.0 and weight > 0.0):
        bmi = float(weight / (height / float(10000)))
        category = bmi_categories(bmi)
        bmi = str(float("{0:.2f}".format(bmi)))
        jarvis.say("Your BMI is : " + bmi)
        jarvis.say("Category : " + category)
    else:
        jarvis.say("Please add positive height(m) and weight(kg)!")
        return None


def bmi_categories(bmi):
    if(bmi < 18.5):
        category = "Underweight"
    elif(bmi < 25):
        category = "Normal weight"
    elif(bmi < 30):
        category = "Overweight"
    else:
        category = "Obesity"
    return category


@plugin("health calories")
def health_calories(jarvis, s):
    """
    Tells the recommended daily calorie intake, also recommends calories for weight add and loss.(Source 1)
    It is based on gender, age, height and weight.
    Uses the Miffin-St Jeor Equation as it is considered the most accurate when we don't know our body fat percentage(Source 2).
    Add gender(man/woman), age(15 - 80 recommended), metric height(cm), weight(kg), workout level(1-4). No decimal weight for now.
    Workout Levels:
        [1] Little or no exersise
        [2] Light 1-3 per week
        [3] Moderate 4-5 per week
        [4] Active daily exersise or physical job
    #Example: health calories woman 27 164 60 3
    ^Sources:
            1) https://en.wikipedia.org/wiki/Basal_metabolic_rate
            2) https://jandonline.org/article/S0002-8223(05)00149-5/fulltext
    """

    strings = s.split()
    if(len(strings) == 5):
        gender = strings[0]
        age = int(strings[1])
        height = int(strings[2])
        weight = float(strings[3])
        level = int(strings[4])
    else:
        jarvis.say("You wrote less or more arguments than it needed.")
        return None

    gender_no = 0
    if(gender == 'man'):
        gender_no = 5
    elif(gender == 'woman'):
        gender_no = -161

    if(gender_no != 0 and age > 14 and height > 0.0 and weight > 0.0 and level > 0 and level < 5):
        brm = float(10 * weight + 6.25 * height - 5 * age + gender_no) * exersise_level(level)
        brm_loss = brm - 500.0
        brm_put_on = brm + 500.0
        jarvis.say("Daily caloric intake :    " + str(brm))
        jarvis.say("Loss weight calories :    " + str(brm_loss))
        jarvis.say("Put on  weight calories : " + str(brm_put_on))
    else:
        jarvis.say("Please add corrent input!")
        return None


def exersise_level(level):
    multiplier = 1
    if(level == 1):
        multiplier = 1.2
    elif(level == 2):
        multiplier = 1.4
    elif(level == 3):
        multiplier = 1.6
    else:
        multiplier = 1.95
    return multiplier
