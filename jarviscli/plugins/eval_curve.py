import sympy
from colorama import Fore
from jarviscli import entrypoint
from jarviscli.plugins.eval import calc, solve_y


@entrypoint
def plot(jarvis, s):
    """
    Plot graph
    -- Example:
        plot x**2
        plot y=x(x+1)(x-1)
    """
    def _plot(expr):
        plots = sympy.plot(expr[0], show=False)

        for i in range(1, len(expr)):
            expr[i] = sympy.plot(expr[i], show=False)
            plots.append(expr[i][0])

        plots.show()
        return ""

    if len(s) == 0:
        jarvis.say("Missing parameter: function (e.g. call 'plot x**2')")
        return

    try:
        calc(jarvis, s, calculator=solve_y, formatter=_plot, do_evalf=False)
    except ValueError:
        jarvis.say("Cannot plot...", Fore.RED)
    except OverflowError:
        jarvis.say("Cannot plot - values probably too big...")
