# -*- coding: utf-8 -*-


class config:
    def __init__(self, core, cli):
        core.addCommandHandler("conf", self, cpriv=10, chelp="Modifica o muestr"
        "a las configuraciones del bot. Sintaxis: key [value]",
        alias=["config"])

    def conf(self, bot, cli, ev):
        if len(ev.splitd) > 1:
            res = bot.writeConf(ev.splitd[0], ev.splitd[1], ev.target)
            if res is True:
                cli.msg(ev.target, "Se ha guardado la configuración")
            else:
                cli.msg(ev.target, "No se pudo guardar la configuración!")
        else:
            cli.msg(ev.target, str(bot.readConf(ev.splitd[0], ev.target)))  # !