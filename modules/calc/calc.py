# -*- coding: utf-8 -*-
import math
import re
import textwrap


class calc:

    def __init__(self, core, client):
        core.addCommandHandler("calc", self, chelp=
        "Calculadora. Sintaxis: calc <cálculo>")

    def calc(self, bot, cli, event):
        res = self.calculate(" ".join(event.splitd))
        if res is None:
            cli.notice(event.target, "No se pudo calcular.")
        else:
            cli.notice(event.target,
            textwrap.wrap(str(res), 500)[0])

    integers_regex = re.compile(r'\b[\d\.]+\b')

    def calculate(self, expr):
        def safe_eval(expr, symbols={}):
            if expr.find("_") != -1:
                return None
            return eval(expr, dict(__builtins__=None), symbols)  # :(

        expr = expr.replace('^', '**')
        return safe_eval(expr, vars(math))
