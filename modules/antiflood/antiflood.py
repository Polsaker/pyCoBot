# -*- coding: utf-8 -*-
from pycobot.tables import User, UserPriv



class authadd:
    def __init__(self, core, client):
        core.addCommandHandler("antiflood", self, cpriv=5, chelp=
        "Maneja el antiflood de un canal. Sintaxis: antiflood <canal> <on/off>"
        " [mensajes] [segundos]", cprivchan=True)

    def antiflood_p(self, bot, cli, ev):
        if len(ev.splitd) > 2:
            return ev.splitd[1]
        else:
            return 0

    def antiflood(self, bot, cli, ev):
        if not len(ev.splitd) > 1:
            cli.privmsg(ev.target, "\00304Error\003: Faltan parametros.")
            return 0
        # TODO.