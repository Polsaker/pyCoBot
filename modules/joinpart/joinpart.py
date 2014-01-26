# -*- coding: utf-8 -*-
import irc.client


class joinpart:

    def __init__(self, core, client):
        core.addCommandHandler("join", self, cpriv=4, chelp=
        "Hace que el bot entre en un canal. Sintaxis: join <canal>",
         cprivchan=True)
        core.addCommandHandler("part", self, cpriv=4, chelp=
        "Hace que el bot salga de un canal. Sintaxis: part [canal] [mensaje]",
         cprivchan=True)

    def join_p(self, bot, cli, event):
        if len(event.splitd) > 0:
            return event.splitd[0]
        return 1

    def join(self, bot, cli, event):
        if len(event.splitd) > 0:
            cli.join(event.splitd[0])
        else:
            cli.privmsg(event.target, "\00304Error\003: Faltan parametros. Si" +
             "ntaxis: join <canal>")

    def part_p(self, bot, cli, event):
        if len(event.splitd) > 0 and irc.client.is_channel(event.splitd[0]):
            return event.splitd[0]
        else:
            return event.target

    def part(self, bot, cli, event):

        if len(event.splitd) > 0:
            chan = event.splitd[0]
            try:
                msg = event.splitd[1]
            except:
                msg = "Salida ordenada por un administrador"
        else:
            msg = "Salida ordenada por un administrador"
            chan = event.target
        cli.part(chan, msg)