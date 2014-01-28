# -*- coding: utf-8 -*-


class joinpart:

    def __init__(self, core, client):
        core.addCommandHandler("say", self, cpriv=1, chelp=
        "Hace que el bot diga algo. Sintaxis: say <canal> <mensaje>",
         cprivchan=True)

    def say_p(self, bot, cli, event):
        if len(event.splitd) > 1:
            return event.splitd[0]
        return 1

    def say(self, bot, cli, event):
        if not len(event.splitd) > 1:
            cli.privmsg(event.target, "\00304Error\003: Faltan parametros. Si" +
             "ntaxis: say <canal> <mensaje>")
            return 1
        cli.privmsg(event.splitd[0], " ".join(event.splitd[1]))
