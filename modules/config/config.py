# -*- coding: utf-8 -*-
import re


class config:
    def __init__(self, core, cli):
        core.addCommandHandler("conf", self, cpriv=10, chelp="Modifica o muestr"
        "a las configuraciones del bot. Sintaxis: key [value]",
        alias=["config"], cprivchan=True)

    def conf_p(self, bot, cli, ev):
        if len(ev.splitd) == 0:
            return
        p1 = re.compile("^channel.*", re.IGNORECASE)
        m1 = p1.search(ev.splitd[0])
        if m1 is not None:
            return ev.target
        else:
            p1 = re.compile("^network\.channels\.(.*)", re.IGNORECASE)
            m1 = p1.search(ev.splitd[0])
            if m1 is not None:
                return m1.group(1)

    def conf(self, bot, cli, ev):
        if len(ev.splitd) == 0:
            cli.msg("\00304Error:\003 Faltan parametros")
            return
        if len(ev.splitd) > 1:
            val = " ".join(ev.splitd[1:])
            res = bot.writeConf(ev.splitd[0], val, ev.target)
            if res is True:
                cli.msg(ev.target, "Se ha guardado la configuración")
            else:
                cli.msg(ev.target, "No se pudo guardar la configuración!")
        else:
            cli.msg(ev.target, str(bot.readConf(ev.splitd[0], ev.target)))  # !