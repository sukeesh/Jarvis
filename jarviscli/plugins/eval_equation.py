# -*- coding: utf-8 -*-

import sympy
from jarviscli import entrypoint
from jarviscli.plugins.eval import calc, format_expression, remove_equals


@entrypoint
def equations(jarvis, term):
    """
    Solves linear equations system

    Use variables: a, b, c, ..., x, y,z

    Example:

    ~> Hi, what can I do for you?
    equations
    1. Equation: x**2 + 2y - z = 6
    2. Equation: (x-1)(y-1) = 0
    3. Equation: y**2 - x -10 = y**2 -y
    4. Equation:
    [{x: -9, y: 1, z: 77}, {x: 1, y: 11, z: 17}]

    """
    a, b, c, d, e, f, g, h, i, j, k, l, m = sympy.symbols(
        'a,b,c,d,e,f,g,h,i,j,k,l,m')
    n, o, p, q, r, s, t, u, v, w, x, y, z = sympy.symbols(
        'n,o,p,q,r,s,t,u,v,w,x,y,z')

    equations = []
    count = 1
    user_input = jarvis.input('{}. Equation: '.format(count))
    while user_input != '':
        count += 1
        user_input = format_expression(user_input)
        user_input = remove_equals(jarvis, user_input)
        equations.append(user_input)
        user_input = jarvis.input('{}. Equation: '.format(count))

    calc(
        jarvis,
        term,
        calculator=lambda expr: sympy.solve(
            expr,
            equations,
            dict=True))
