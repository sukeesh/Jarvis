from plugin import plugin


@plugin("check simple expression")
def expression_checker(jarvis, s):
    validCharacters = "()+-*/0123456789"
    digits = "0123456789"
    operators = "+-*/"
    brackets = "()"

    while True:
        expression = input("Enter Expression To Analyze : ")
        while len(expression.strip()) == 0:
            expression = input("Expression Length is 0 , Enter Again : ")
        if expression.lower() == "stop":
            print("You Terminated Expression Checker! Bye!")
            break
        terminateCurrentAnalyzation = 0
        for character in expression:
            if character not in validCharacters:
                print("Not Valid Expression! Invalid Character : " + character)
                terminateCurrentAnalyzation = 1
                break

        previousIsOperator = 0
        previousIsDigit = 0
        previousIsOpenBracket = 0
        previousIsCloseBracket = 0
        for character in expression:
            if character in operators:
                if previousIsOperator or previousIsOpenBracket:
                    print("Not Valid Expression! Invalid Expression Character Progression")
                    terminateCurrentAnalyzation = 1
                    break
                previousIsOperator = 1
                previousIsDigit = 0
                previousIsOpenBracket = 0
                previousIsCloseBracket = 0
            elif character in digits:
                if previousIsCloseBracket:
                    print("Not Valid Expression! Invalid Expression Character Progression")
                    terminateCurrentAnalyzation = 1
                    break
                previousIsOperator = 0
                previousIsDigit = 1
                previousIsOpenBracket = 0
                previousIsCloseBracket = 0
            elif character == '(':
                if previousIsDigit or previousIsCloseBracket:
                    print("Not Valid Expression! Invalid Expression Character Progression")
                    terminateCurrentAnalyzation = 1
                    break
                previousIsOperator = 0
                previousIsDigit = 0
                previousIsOpenBracket = 1
                previousIsCloseBracket = 0
            elif character == ')':
                if previousIsOperator or previousIsOpenBracket:
                    print("Not Valid Expression! Invalid Expression Character Progression")
                    terminateCurrentAnalyzation = 1
                    break
                previousIsOperator = 0
                previousIsDigit = 0
                previousIsOpenBracket = 0
                previousIsCloseBracket = 1
        stack = []
        for character in expression:
            if character == ')':
                if len(stack) == 0:
                    print("Not Valid Expression! Invalid Bracket Progression")
                    terminateCurrentAnalyzation = 1
                    break
                else:
                    picked = stack.pop()
                    if picked == '(':
                        continue
                    else:
                        stack.append(picked)
                        stack.append(character)
            elif character == '(':
                stack.append(character)
        if len(stack) != 0:
            print("Not Valid Expression! Invalid Bracket Progression")
            terminateCurrentAnalyzation = 1
        if terminateCurrentAnalyzation:
            continue
        print("Expression Is Valid!")
