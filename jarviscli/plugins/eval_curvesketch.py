import sympy
from colorama import Fore
from jarviscli import entrypoint
from jarviscli.plugins.eval import format_expression, remove_equals, solve_y


@entrypoint
def curvesketch(jarvis, s):
    """
    Prints useful information about a graph of a function.
    * Limit
    * Intersection x/y axis
    * Derivative and Integral
    * Minima / Maxima / Turning point
    -- Example:
        curve sketch y=x**2+10x-5
        curve sketch y=sqrt((x+1)(x-1))
        curve sketch y=1/3x**3-2x**2+3x
    """
    if len(s) == 0:
        jarvis.say(
            "Missing parameter: function (e.g. call 'curve sketch y=x**2+10x-5')")
        return

    def section(jarvis, headline):
        jarvis.say("\n{:#^50}".format(" {} ".format(headline)), Fore.MAGENTA)

    term = remove_equals(jarvis, s)
    term = format_expression(term)
    term = solve_y(jarvis, term)

    def get_y(x_val, func=term):
        x = sympy.Symbol('x')
        return func.evalf(subs={x: x_val})

    section(jarvis, s)

    section(jarvis, "Graph")
    jarvis.eval('plot {}'.format(s))

    section(jarvis, "Limit")
    jarvis.eval('limit {}'.format(term))

    section(jarvis, "Intersection x-axis")
    jarvis.eval('solve {}'.format(term))

    section(jarvis, "Intersection y-axis")
    jarvis.say(str(get_y(0).round(9)), Fore.BLUE)

    section(jarvis, "Factor")
    jarvis.eval('factor {}'.format(term))

    section(jarvis, "Derivative")
    x = sympy.Symbol('x')
    derivative_1 = sympy.Derivative(term, x).doit()
    derivative_2 = sympy.Derivative(derivative_1, x).doit()
    derivative_3 = sympy.Derivative(derivative_2, x).doit()
    jarvis.say("1. Derivative: {}".format(derivative_1), Fore.BLUE)
    jarvis.say("2. Derivative: {}".format(derivative_2), Fore.BLUE)
    jarvis.say("3. Derivative: {}".format(derivative_3), Fore.BLUE)

    section(jarvis, "Integral")
    jarvis.say("F(x) = {} + t".format(sympy.Integral(term, x).doit()), Fore.BLUE)

    section(jarvis, "Maxima / Minima")
    try:
        critical_points = sympy.solve(derivative_1)
    except NotImplementedError:
        jarvis.say("Sorry, cannot solve...", Fore.RED)
        critical_points = []

    for x in critical_points:
        y = str(get_y(x).round(9))

        try:
            isminmax = float(get_y(x, func=derivative_2))
        except ValueError:
            isminmax = None
        except TypeError:
            # probably complex number
            isminmax = None

        if isminmax is None:
            minmax = "unknown"
        elif isminmax > 0:
            minmax = "Minima"
        elif isminmax < 0:
            minmax = "Maxima"
        else:
            minmax = "/"

        jarvis.say("({}/{}) : {}".format(x, y, minmax), Fore.BLUE)

    section(jarvis, "Turning Point")
    try:
        critical_points = sympy.solve(derivative_2)
    except NotImplementedError:
        jarvis.say("Sorry, cannot solve...", Fore.RED)
        critical_points = []

    for x in critical_points:
        y = get_y(x)

        try:
            is_turning_point = float(get_y(x, func=derivative_3))
        except ValueError:
            is_turning_point = -1

        if is_turning_point != 0:
            jarvis.say("({}/{})".format(x, y.round(9)), Fore.BLUE)

    section(jarvis, "")
