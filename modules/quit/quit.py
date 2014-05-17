# -*- coding: utf-8 -*-y
import os


class quit:

    def __init__(self, core, cli):
        self.core = core
        core.addCommandHandler("quit", self, cpriv=10, chelp="Hace que el bot s"
        "alga de un servidor. Sintaxis: quit [servidor] [mensaje]")
        core.addCommandHandler("close", self, cpriv=10, chelp="Cierra el bot.")
        core.addCommandHandler("reconnect", self, cpriv=9, chelp="Reconecta al"
        "bot de un servidor. Sintaxis: reconnect [servidor] [mensaje]")
        core.addCommandHandler("restart", self, cpriv=10, chelp="Reinicia al "
        " bot. Sintaxis: restart <mensaje>")

    def close(self, bot, cli, event):
        if len(event.splitd) > 0:
            quitmsg = " ".join(event.splitd)
        else:
            quitmsg = "Salida ordenada por un administrador"
        for i in enumerate(self.core.botcli.boservers):
            i[1].server.quit("[QUIT] " + quitmsg)
        os._exit(0)

    def quit(self, bot, cli, event):
        servquit = bot
        if len(event.splitd) > 0:
            quitmsg = " ".join(event.splitd)
            for server in bot.botcli.boservers:
                if server.sid == event.splitd[0]:
                    servquit = server
                    if len(event.splitd) > 1:
                        quitmsg = " ".join(event.splitd[1:])
                    else:
                        quitmsg = "Salida ordenada por un administrador"
        else:
            quitmsg = "Salida ordenada por un administrador"

        servquit.server.disconnect("[QUIT] " + quitmsg)
        #for i in enumerate(self.core.botcli.boservers):
        #    i[1].server.quit("[QUIT] " + quitmsg)
        #os._exit(0)

    def reconnect(self, bot, cli, event):
        servquit = bot
        if len(event.splitd) > 0:
            quitmsg = " ".join(event.splitd)
            for server in bot.botcli.boservers:
                if server.sid == event.splitd[0]:
                    servquit = server
                    if len(event.splitd) > 1:
                        quitmsg = " ".join(event.splitd[1:])
                    else:
                        quitmsg = "Salida ordenada por un administrador"
        else:
            quitmsg = "Salida ordenada por un administrador"
        bot.botcli.nocheck = True
        servquit.server.disconnect("[QUIT] " + quitmsg)
        servquit.server.connect(servquit.readConf("network.server"),
                        servquit.readConf("network.port"),
                        servquit.readConf("network.nick"),
                        servquit.readConf("network.nick"),
                        servquit.server.gecos)
        bot.botcli.nocheck = False

    def restart(self, bot, cli, event):
        if len(event.splitd) > 0:
            quitmsg = " ".join(event.splitd)
        else:
            quitmsg = "Salida ordenada por un administrador"
        bot.restart_program("[RESTART] " + quitmsg)
