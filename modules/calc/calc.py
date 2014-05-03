# -*- coding: utf-8 -*-
import math
import re
import textwrap
import multiprocessing


class calc:

    def __init__(self, core, client):
        core.addCommandHandler("calc", self, chelp=
        "Calculadora. Sintaxis: calc <cálculo>")
        self.res = None
        self.q = multiprocessing.Queue()

    def calc(self, bot, cli, event):
        #res = self.calculate(" ".join(event.splitd))

        res = self.try_slow_thing(self.calculate,
                                " ".join(event.splitd), self.q)
        if res is None:
            cli.notice(event.target, "No se pudo calcular.")
        else:
            restr = "%.64f" % res
            restr = self.adjust_decimals(restr)
            restr = self.adjust_decimals(restr)
            cli.notice(event.target,
            textwrap.wrap(restr, 400)[0])

    def adjust_decimals(self, s):
        i = 0
        while i != len(s):
            ik = i + 1
            if s[len(s) - ik:len(s) - i] == "0":
                s = s[0:len(s) - ik]
            elif s[len(s) - ik:len(s) - i] == ".":
                s = s[0:len(s) - ik]
                return s
            else:
                return s
            i += 1
        return s

    integers_regex = re.compile(r'\b[\d\.]+\b')

    def calculate(self, expr, q):
        def safe_eval(expr, symbols={}):
            if expr.find("_") != -1:
                return None
            try:
                return eval(expr, dict(__builtins__=None), symbols)  # :(
            except:
                return "Error de sintaxis o algo por el estilo."

        expr = expr.replace('^', '**')
        vrs = vars(math)
        vrs['cosd'] = cosd
        vrs['tand'] = tand
        vrs['sind'] = sind
        q.put(safe_eval(expr, vrs))

    def try_slow_thing(self, function, *args):
        p = multiprocessing.Process(target=function, args=args)
        p.start()
        p.join(5)
        if p.is_alive():
            p.terminate()
            return "La operación se ha demorado mucho en finalizar"
        else:
            return self.q.get(True)


def cosd(x):
    return math.cos(x * math.pi / 180)


def tand(x):
    return math.tan(x * math.pi / 180)


def sind(x):
    return math.sin(x * math.pi / 180)