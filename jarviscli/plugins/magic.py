import random
from plugin import plugin


@plugin('magic')
def magic(jarvis, s):
    greetings = "############################################\n" \
                "#               GREETINGS!                 #\n" \
                "#  Absolute Magic Is Going To Happen Here! #\n" \
                "############################################\n"
    print(greetings)

    while 1:
        numbers = []
        operators = []

        desire = 0
        while desire != 1:
            print("Pick Any Number And Remember!")
            input("")
            numSteps = 0
            while 1:
                if numSteps > 5:
                    randomInd = random.randint(1, 3)
                    if randomInd == 1:
                        answer = input("Its Over Now! Tell Me Answer And I'll Tell You Your Number! : ")
                        for index, operator in reversed(list(enumerate(operators))):
                            if operator == "+":
                                answer = answer - numbers[index]
                            elif operator == "-":
                                answer = answer + numbers[index]
                            elif operator == "*":
                                answer = answer / numbers[index]
                            elif operators == "/":  # /
                                answer = answer * numbers[index]
                        print("Your Number Was " + str(answer) + " If You Did Not Cheat!")
                        desireString = input("Do You Want To Do It Again? (Y/N) : ")
                        if desireString == "N":
                            desire = 1
                        break

                operatorInd = random.randint(1, 5)  # [1-4]
                randomNum = random.randint(1, 100)
                if operatorInd == 1:  # +
                    operators.append("+")
                    print("Add " + str(randomNum) + " To Your Calculation")
                    input("")
                elif operatorInd == 2:  # -
                    operators.append("-")
                    print("Subtract " + str(randomNum) + " from Your Calculation")
                    input("")
                elif operatorInd == 3:  # *
                    operators.append("*")
                    print("Multiply Your Calculation By " + str(randomNum))
                    input("")
                elif operatorInd == 4:  # /
                    operators.append("/")
                    print("Divide Your Calculation By " + str(randomNum))
                    input("")
                numbers.append(randomNum)
