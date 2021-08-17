from plugin import plugin
import random


@plugin("give me advice")
def advice(jarvis, s):
    answers = [
        "No",
        "Yes",
        "You Can Do It!",
        "I Cant Help You",
        "Sorry To hear That, But You Must Forget :(",
        "Keep It Up!",
        "Nice",
        "Dont Do It Ever Again",
        "I Like It, Good Job",
        "I Am Not Certain",
        "Too Bad For You, Try To Find Something Else To Do And Enjoy",
        "Time Will Pass And You Will Forget",
        "Dont Do It",
        "Do It",
        "Never Ask Me About That Again",
        "I Cant Give Advice Now I Am Sleepy",
        "Sorry I Cant Hear This Language",
        "Sorry But Your Question Does Not Make Sense"]

    greetings = "#################################################\n" \
                "#                   HELLO THERE!                #\n" \
                "#   Ask Me Question And I Will Give You Advice  #\n" \
                "# I Am Limited So Pick First Which Fits Context #\n" \
                "#################################################\n"
    question = ""
    acceptable = 0
    while not acceptable:
        question = input("Ask Me A Question : ")
        questionTmp = question.strip()
        if len(questionTmp) > 0:
            if questionTmp[len(questionTmp) - 1] == '?':
                acceptable = 1

    while True:
        randPos = random.randint(0, len(answers))
        print(answers[randPos])
        indicator = 0
        while True:
            desire = input("Was This In Context? (Y/N) : ")
            if desire.strip().lower() == 'n':
                print("Its A Pitty :( I'll Try Again!")
                break
            elif desire.strip().lower() == 'y':
                indicator = 1
                print("Good To hear! Happy To Advice You!")
                break
            else:
                continue
        if indicator == 1:
            print("Good Bye!")
            break
