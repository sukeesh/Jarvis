import sympy
from colorama import Fore
from jarviscli import entrypoint
from jarviscli.plugins.eval import format_expression, remove_equals, solve_y


@entrypoint
def limit(jarvis, s):
    """
    Prints limit to +/- infinity or to number +-. Use 'x' as variable.
    -- Examples:
        limit 1/x
        limit @1 1/(1-x)
        limit @1 @2 1/((1-x)(2-x))
    """
    def try_limit(term, x, to, directory=''):
        try:
            return sympy.Limit(term, x, to, directory).doit()
        except sympy.SympifyError:
            return 'Error'
        except NotImplementedError:
            return "Sorry, cannot solve..."

    if s == '':
        jarvis.say("Usage: limit TERM")
        return

    s_split = s.split()
    limit_to = []
    term = ""
    for token in s_split:
        if token[0] == '@':
            if token[1:].isnumeric():
                limit_to.append(int(token[1:]))
            else:
                jarvis.say("Error: {} Not a number".format(
                    token[1:]), Fore.RED)
        else:
            term += token

    term = remove_equals(jarvis, term)
    term = format_expression(term)

    try:
        term = solve_y(jarvis, term)
    except (sympy.SympifyError, TypeError):
        jarvis.say('Error, not a valid term')
        return

    x = sympy.Symbol('x')

    # infinity:
    jarvis.say("lim ->  ∞\t= {}".format(try_limit(term,
                                                  x, +sympy.S.Infinity)), Fore.BLUE)
    jarvis.say("lim -> -∞\t= {}".format(try_limit(term,
                                                  x, -sympy.S.Infinity)), Fore.BLUE)

    for limit in limit_to:
        limit_plus = try_limit(term, x, limit, directory="+")
        limit_minus = try_limit(term, x, limit, directory="-")

        jarvis.say("lim -> {}(+)\t= {}".format(limit, limit_plus), Fore.BLUE)
        jarvis.say("lim -> {}(-)\t= {}".format(limit, limit_minus), Fore.BLUE)
