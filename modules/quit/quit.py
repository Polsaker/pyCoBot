# -*- coding: utf-8 -*-
import os


class quit:

    def __init__(self, core, cli):
        self.core = core
        core.addCommandHandler("quit", self, cpriv=10)
        core.addCommandHandler("reconnect", self, cpriv=9)
        core.addCommandHandler("restart", self, cpriv=10)

    def quit(self, bot, cli, event):
        if len(event.splitd) > 0:
            quitmsg = " ".join(event.splitd)
        else:
            quitmsg = "Salida ordenada por un administrador"
        for i in enumerate(self.core.botcli.boservers):
            i[1].server.quit("[QUIT] " + quitmsg)

        os._exit(0)

    def reconnect(self, bot, cli, event):
        if len(event.splitd) > 0:
            quitmsg = " ".join(event.splitd)
        else:
            quitmsg = "Salida ordenada por un administrador"
        cli.quit("[RECONNECT] " + quitmsg)
        cli.reconnect()

    def restart(self, bot, cli, event):
        if len(event.splitd) > 0:
            quitmsg = " ".join(event.splitd)
        else:
            quitmsg = "Salida ordenada por un administrador"
        bot.restart_program("[RESTART] " + quitmsg)