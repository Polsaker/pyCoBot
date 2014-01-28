# -*- coding: utf-8 -*-


class raw:

    def __init__(self, core, client):
        core.addCommandHandler("raw", self, cpriv=10,
        chelp="Envía información raw al servidor. Sintaxis: raw <texto>")

    def raw(self, bot, cli, ev):
        cli.send_raw(" ".join(ev.splitd))