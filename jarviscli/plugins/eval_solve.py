import sympy
from jarviscli import entrypoint
from jarviscli.plugins.eval import calc, remove_equals


@entrypoint
def solve(jarvis, s):
    """
    Prints where expression equals zero
    -- Example:
        solve x**2 + 5*x + 3
        solve x + 3 = 5
    """
    x = sympy.Symbol('x')

    def _format(solutions):
        if solutions == 0:
            return "No solution!"
        ret = ''
        for count, point in enumerate(solutions):
            if x not in point:
                return "Please use 'x' in expression."
            x_value = point[x]
            ret += "{}. x: {}\n".format(count, x_value)
        return ret

    def _calc(expr):
        return sympy.solve(expr, x, dict=True)

    s = remove_equals(jarvis, s)
    calc(jarvis, s, calculator=_calc, formatter=_format, do_evalf=False)
