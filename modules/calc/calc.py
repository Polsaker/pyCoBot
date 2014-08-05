# -*- coding: utf-8 -*-
import math
import re
import textwrap
import multiprocessing
import sys
try:
    from mpmath import mp
except:
    pass


class calc:

    def __init__(self, core, client):
        core.addCommandHandler("calc", self, chelp="calc.help")
        self.res = None
        self.q = multiprocessing.Queue()
        self.vrs = vars(math)
        try:
            mp
            self.vrs = vars(mp)
            mp.dps = 128
            core.addCommandHandler("calcdps", self, cpriv=2, chelp=
                "Ajusta la cantidad de decimales que mostrara calc. Sintaxis:"
                                                            " calcdps <numero>")
        except:
            pass
        self.vrs['cosd'] = cosd
        self.vrs['tand'] = tand
        self.vrs['sind'] = sind

    def calcdps(self, bot, cli, ev):
        from mpmath import mp
        mp.dps = int(ev.splitd[0])
        cli.msg(ev.source, bot._(ev, self, "calcdps").format(ev.splitd[0]))

    def calc(self, bot, cli, event):
        #res = self.calculate(" ".join(event.splitd))

        res = self.try_slow_thing(self.calculate,
                                " ".join(event.splitd), self.q, bot, event)
        if res is None:
            cli.msg(event.target, bot._(event, self, "calcerr"))
        else:
            restr = res
            restr = self.adjust_decimals(restr)
            restr = self.adjust_decimals(restr)
            cli.msg(event.target,
            textwrap.wrap(restr, 800)[0])

    def adjust_decimals(self, s):
        if "." not in s:
            return s
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

    def calculate(self, expr, q, bot, ev):
        def safe_eval(expr, symbols={}):
            if expr.find("_") != -1:
                return None
            try:
                return eval(expr, dict(__builtins__=None), symbols)  # :(
            except:
                e = sys.exc_info()[0]
                return bot._(ev, self, "syntaxerror".format(str(e))

        expr = expr.replace('^', '**')

        resp = safe_eval(expr, self.vrs)
        try:
            resp = mp.nstr(resp, mp.dps, min_fixed=-mp.inf)
        except:
            pass

        q.put(str(resp))

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
    try:
        return mp.cos(x * mp.pi / 180)
    except:
        return math.cos(x * math.pi / 180)


def tand(x):
    try:
        return mp.tan(x * mp.pi / 180)
    except:
        return math.tan(x * math.pi / 180)


def sind(x):
    try:
        return mp.sin(x * mp.pi / 180)
    except:
        return math.sin(x * math.pi / 180)
