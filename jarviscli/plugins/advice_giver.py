import random
from plugin import plugin

ANSWERS = [
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
  "Sorry But Your Question Does Not Make Sense"
]


@plugin("give me advice")
def advice(jarvis, s):
    while True:
        question = input("Ask Me A Question : ").strip()
        if len(question) > 0 and question[-1] == '?':
            break
        else:
            print("Questions should end with a question mark: ?")

    while True:
        random_idx = random.randint(0, len(ANSWERS))
        print(ANSWERS[random_idx])

        while True:
            desire = input("Was This In Context? (Y/N) : ")
            if desire.strip().lower() == 'n':
                print("Its A Pitty :( I'll Try Again!")
                break
            elif desire.strip().lower() == 'y':
                print("Good To hear! Happy To Advice You!")
                print("Good Bye!")
                return
