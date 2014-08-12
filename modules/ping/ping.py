# -*- coding: utf-8 -*-
import time
import locale


class ping:

    def __init__(self, core, client):
        core.addCommandHandler("ping", self, chelp="ping.help")
        core.addCommandHandler("pong", self)
        core.addCommandHandler("pig", self)
        core.addCommandHandler("lag", self, chelp="lag.help")
        core.addHandler("ctcpreply", self, "pingrep")

    def pig(self, bot, cli, event):
        cli.msg(event.target, bot._(event, self, "pog").format(event.source))

    def ping(self, bot, cli, event):
        cli.msg(event.target, event.source + ": pong")

    def pong(self, bot, cli, event):
        cli.msg(event.target, event.source + ": ping")

    def lag(self, bot, cli, event):
        current_milli_time = int(round(time.time() * 1000))
        cli.privmsg(event.source, "\1PING %s\1" % current_milli_time)
        self.chan = event.target

    def pingrep(self, client, event):
        if not event.arguments[0] == "PING":
            return 0
        current_milli_time = int(round(time.time() * 1000))
        diff = current_milli_time - int(event.arguments[1])
        secs = locale.str(diff / 1000)  # milisegudos -> segundos
        client.msg(self.chan, bot._(event, self, "lag").format(event.source, secs))
