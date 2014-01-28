# -*- coding: utf-8 -*-
import os
import logging
import json


class quit:

    def __init__(self, core, cli):
        self.core = core
        core.addCommandHandler("quit", self, cpriv=10, chelp="Cierra el bot. "
        "Sintaxis: quit <mensaje>")
        core.addCommandHandler("reconnect", self, cpriv=9, chelp="Reconecta al"
        "bot del servidor actual. Sintaxis: reconnect <mensaje>")
        core.addCommandHandler("restart", self, cpriv=10, chelp="Reinicia al "
        " bot. Sintaxis: restart <mensaje>")
        core.addCommandHandler("rehash", self, cpriv=9, chelp="Relee los "
        "archivos de configuración.")

    def quit(self, bot, cli, event):
        if len(event.splitd) > 0:
            quitmsg = " ".join(event.splitd)
        else:
            quitmsg = "Salida ordenada por un administrador"
        for i in enumerate(self.core.botcli.boservers):
            i[1].server.quit("[QUIT] " + quitmsg)
        os._exit(0)

    def rehash(self, bot, cli, event):
        logging.info("Re-cargando archivos de configuracion")
        try:
            jsonConf = open("pycobot.conf").read()
            conf = json.loads(jsonConf)
        except:
            logging.error('No se ha podido abrir el archivo de configuración')
            cli.privmsg(event.target, "\00304Error\003: No se han podido "
            "abrir los archivos de configuración")
            return 0

        for k, l in enumerate(self.core.botcli.boservers):
            k.mconf = conf
            conf['irc'][k.sid]['pserver'] = conf['irc'][k]['server'] \
             .replace(".", "")
            k.conf = conf['irc'][k.sid]
        cli.privmsg(event.target, "Se han recargado las configuraciones.")

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