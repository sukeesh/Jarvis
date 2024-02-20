import re

import sympy
from colorama import Fore


def remove_equals(jarvis, equation):
    """
    User should be able to input equations like x + y = 1.
    SymPy only accepts equations like: x + y - 1 = 0.
    => This method Finds '=' and move everything beyond to left side
    """
    split = equation.split('=')
    if len(split) == 1:
        return equation
    if len(split) != 2:
        jarvis.say("Warning! More than one = detected!", Fore.RED)
        return equation

    return "{} - ({})".format(split[0], split[1])


def format_expression(s):
    s = str.lower(s)
    s = s.replace("power", "**")
    s = s.replace("plus", "+")
    s = s.replace("minus", "-")
    s = s.replace("dividedby", "/")
    s = s.replace("by", "/")
    s = s.replace("^", "**")

    # Insert missing * commonly omitted
    # 2x -> 2*x
    p = re.compile('(\\d+)([abcxyz])')
    s = p.sub(r'\1*\2', s)

    # x(... -> x*(...
    p = re.compile('([abcxyz])\\(')
    s = p.sub(r'\1*(', s)

    # (x-1)(x+1) -> (x-1)*(x+1)
    # x(... -> x*(...
    s = s.replace(")(", ")*(")

    return s


def solve_y(jarvis, s):
    if 'y' in s:
        symbol = sympy.Symbol('y')
    elif 'x' in s and '=' in s:
        symbol = sympy.Symbol('x')
    else:
        return solve_y(jarvis, "({}) -y".format(s))

    s = remove_equals(jarvis, s)

    try:
        results = sympy.solve(s, symbol)
    except NotImplementedError:
        return 'unknown'

    if len(results) == 0:
        return '0'
    else:
        return results


def calc(jarvis, s, calculator=sympy.sympify, formatter=None, do_evalf=True):
    s = format_expression(s)

    try:
        result = calculator(s)
    except sympy.SympifyError:
        jarvis.say("Error: Something is wrong with your expression", Fore.RED)
        return
    except NotImplementedError:
        jarvis.say("Sorry, cannot solve", Fore.RED)
        return

    if formatter is not None:
        if 'x' in s and '=' in s and 'y' not in s:
            x = sympy.Symbol('x')
            result = sympy.plotting.plot_implicit(
                sympy.Eq(x, result[0]), (x, result[0] - 5, result[0] + 5))
        else:
            result = formatter(result)

    if do_evalf:
        result = result.evalf()

    jarvis.say(str(result), Fore.BLUE)
