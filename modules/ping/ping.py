# -*- coding: utf-8 -*-
import time


class ping:

    def __init__(self, core, client):
        core.addCommandHandler("ping", self, chelp="Responde con pong.")
        core.addCommandHandler("pong", self, chelp="Responde con ping.")
        core.addCommandHandler("lag", self, chelp="Mide el lag.")
        core.addHandler("ctcpreply", self, "pingrep")

    def ping(self, bot, cli, event):
        cli.privmsg(event.target, event.source + ": pong")

    def pong(self, bot, cli, event):
        cli.privmsg(event.target, event.source + ": ping")

    def lag(self, bot, cli, event):
        current_milli_time = int(round(time.time() * 1000))
        cli.privmsg(event.source, "\1PING %s\1" % current_milli_time)
        self.chan = event.target

    def pingrep(self, client, event):
        if not event.arguments[0] == "PING":
            return 0
        current_milli_time = int(round(time.time() * 1000))
        diff = current_milli_time - int(event.arguments[1])
        secs = str(diff / 1000)  # milisegudos -> segundos
        client.privmsg(self.chan, event.source + " tiene un lag de " + secs +
        " segundos.")