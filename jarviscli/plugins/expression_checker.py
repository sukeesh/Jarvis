from plugin import plugin


@plugin("check simple expression")
def expression_checker(jarvis, s):
    validCharacters = "()+-*/0123456789"
    digits = "0123456789"
    operators = "+-*/"
    brackets = "()"

    def is_empty_expression(expr):
        return len(expr.strip()) == 0

    def contains_invalid_characters(expr):
        return any(char not in validCharacters for char in expr)

    def check_character_progression(expr):
        previousIsOperator = previousIsDigit = previousIsOpenBracket = previousIsCloseBracket = 0
        
        for char in expr:
            if char in operators:
                if previousIsOperator or previousIsOpenBracket:
                    return False
                previousIsOperator, previousIsDigit = 1, 0
                previousIsOpenBracket, previousIsCloseBracket = 0, 0
            elif char in digits:
                if previousIsCloseBracket:
                    return False
                previousIsOperator, previousIsDigit = 0, 1
                previousIsOpenBracket, previousIsCloseBracket = 0, 0
            elif char == '(':
                if previousIsDigit or previousIsCloseBracket:
                    return False
                previousIsOperator, previousIsDigit = 0, 0
                previousIsOpenBracket, previousIsCloseBracket = 1, 0
            elif char == ')':
                if previousIsOperator or previousIsOpenBracket:
                    return False
                previousIsOperator, previousIsDigit = 0, 0
                previousIsOpenBracket, previousIsCloseBracket = 0, 1
        return True

    def check_bracket_pairs(expr):
        stack = []
        for char in expr:
            if char == '(':
                stack.append(char)
            elif char == ')':
                if not stack:
                    return False
                stack.pop()
        return len(stack) == 0

    while True:
        expression = input("Enter Expression To Analyze : ")
        while is_empty_expression(expression):
            expression = input("Expression Length is 0 , Enter Again : ")
            
        if expression.lower() == "stop":
            print("You Terminated Expression Checker! Bye!")
            break

        if contains_invalid_characters(expression):
            print(f"Not Valid Expression! Invalid Character found")
            continue

        if not check_character_progression(expression):
            print("Not Valid Expression! Invalid Expression Character Progression")
            continue

        if not check_bracket_pairs(expression):
            print("Not Valid Expression! Invalid Bracket Progression")
            continue

        print("Expression Is Valid!")
