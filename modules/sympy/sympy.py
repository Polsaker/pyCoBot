# -*- coding: utf-8 -*-

import logging
try:
    from sympy.solvers import solve
    from sympy import Symbol
    from sympy.core import sympify
except ImportError:
    logging.error("m_sympy: Sympy no está instalado.")


class sympy:
    def __init__(self, core, client):
        try:
            solve
        except:
            return

        core.addCommandHandler("calcx", self, chelp="Resuelve X en una ecuación"
            ". Sintaxis: calcx <ecuación>")
        core.addCommandHandler("calcxy", self, chelp="Resuelve X e Y en una ecu"
            "ación. Sintaxis: calcxy <ecuación>")

    def calcx(self, bot, cli, ev):
        if len(ev.splitd) < 1:
            cli.msg("Error: Faltan parametros")

        expr = " ".join(ev.splitd)

        expr = expr.replace("=", "-")

        pr = sympify(expr)
        x = Symbol('x')
        res = solve(pr, x)
        cli.msg(ev.target, res)

    def calcxy(self, bot, cli, ev):
        if len(ev.splitd) < 1:
            cli.msg("Error: Faltan parametros")

        expr = " ".join(ev.splitd)
        expr = "(" + expr
        expr = expr.replace("=", ") - (")
        expr = expr + ")"
        try:
            pr = sympify(expr)
        except:
            cli.msg(ev.target, "Error de sintaxis o algo por el estilo.")
            return 0
        x = Symbol('x')
        y = Symbol('y')
        res = solve(pr, x, y)
        cli.msg(ev.target, res)
