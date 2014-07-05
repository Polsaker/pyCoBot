# -*- coding: utf-8 -*-
import irc.client
import time


class autoprotect:

    def __init__(self, core, client):
        core.addHandler("mode", self, "modeprot")
        core.addHandler("join", self, "jchan")
        core.addHandler("kick", self, "kickrejoin")
        core.addHandler("480", self, "rejoin")  # +j
        core.addHandler("bannedfromchan", self, "unban")
        core.addHandler("inviteonlychan", self, "invite")
        self.tries = 0

    def jchan(self, cli, ev):
        if irc.client.parse_nick(ev.source)[1] == cli.nickname:
            self.tries = 0

    def invite(self, cli, ev):
        if ev.target == cli.nickname:
            if self.tries < 20:
                cli.privmsg("ChanServ", "INVITE " + ev.arguments[0])
                cli.join(ev.arguments[0])
                self.tries = self.tries + 1

    def unban(self, cli, ev):
        if ev.target == cli.nickname:
            if self.tries < 20:
                cli.privmsg("ChanServ", "UNBAN " + ev.arguments[0])
                cli.join(ev.arguments[0])
                self.tries = self.tries + 1

    def modeprot(self, cli, ev):
        if self.parsemode(cli, ev) is True:
            cli.privmsg("ChanServ", "OP " + ev.target)

    def kickrejoin(self, cli, ev):
        if ev.arguments[0] == cli.nickname:
            time.sleep(2)
            cli.join(ev.target)
            
    def rejoin(self, cli, ev):
        time.sleep(2)
        cli.join(ev.target)
        

    # parse modestack
    # Parcialmente, ya que nosotros solo le prestamos atención cuando se QUITA
    # un modo y no cuando se aplica..
    def parsemode(self, cli, ev):
        cmodelist = cli.features.chanmodes
        param = cmodelist[0] + cmodelist[1] + cmodelist[2]
        for i, val in enumerate(cli.features.prefix):
            param = param + cli.features.prefix[val]
        pos = 0
        for c in ev.arguments[0]:
            if c == "+":
                rving = False
                pass  # D:
            elif c == "-":
                rving = True
            else:
                if c in param:
                    pos = pos + 1
            if rving is False:
                continue

            if c == "o" and ev.arguments[pos] == cli.nickname:
                return True  # BEEP BEEP BEEP BEEP
        return False
