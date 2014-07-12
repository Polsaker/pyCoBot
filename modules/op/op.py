# -*- coding: utf-8 -*-
import irc.client
import re
import time


class op:
    def __init__(self, core, client):
        core.addCommandHandler("op", self, cpriv=5, cprivchan=True, chelp=
        "Da op en un canal. Sintaxis: op [canal] [nick]", alias=['o'])
        core.addCommandHandler("deop", self, cpriv=5, cprivchan=True, chelp=
        "Quita op en un canal. Sintaxis: deop [canal] [nick]")
        core.addCommandHandler("voice", self, cpriv=3, cprivchan=True, chelp=
        "Da voz en un canal. Sintaxis: voice [canal] [nick]", alias=['v'])
        core.addCommandHandler("devoice", self, cpriv=3, cprivchan=True, chelp=
        "Quita voz en un canal. Sintaxis: devoice [canal] [nick]")
        core.addCommandHandler("kick", self, cpriv=4, cprivchan=True, chelp=
        "Expusa a alguien de un canal. Sintaxis: kick [canal] [nick]",
         alias=['k'])
        core.addCommandHandler("kickban", self, cpriv=4, cprivchan=True, chelp=
        "Banea a alguien de un canal. Sintaxis: kickban [canal] [nick]",
         alias=['kb', 'ban'])
        core.addCommandHandler("timedban", self, cpriv=4, cprivchan=True, chelp=
        "Banea a alguien de un canal por un tiempo determinado. Sintaxis: "
        "kickban [canal] [nick] [tiempo en minutos]", alias=['tb', 'tban'])
        core.addCommandHandler("unban", self, cpriv=3, cprivchan=True, chelp=
        "Des-banea a alguien de un canal. Sintaxis: unban [canal] [nick]",
        alias=['ub'])
        core.addCommandHandler("topic", self, cpriv=4, cprivchan=True, chelp=
        "Cambia el topic de un canal. Sintaxis: topic [canal] [topic]")

        core.addHandler("whoreply", self, "whoban")
        core.addHandler("banlist", self, "banlist")
        self.masc = None
        self.actn = False
        self.core = core

    def op_p(self, bot, cli, ev):
        if len(ev.splitd) > 0 and irc.client.is_channel(ev.splitd[0]):
            return ev.splitd[0]
        else:
            return ev.target

    def _getchannick(self, ev, tb=False):
        restofthestuff = None
        if len(ev.splitd) > 0 and irc.client.is_channel(ev.splitd[0]):
            chan = ev.splitd[0]
            if len(ev.splitd) > 1:
                nick = ev.splitd[1]
                if tb is False:
                    atr = " ".join(ev.splitd[2:])
                else:
                    restofthestuff = ev.splitd[2]
                    atr = " ".join(ev.splitd[3:])
            else:
                nick = ev.source
                if tb is False:
                    atr = " ".join(ev.splitd[1:])
                else:
                    restofthestuff = ev.splitd[1]
                    atr = " ".join(ev.splitd[2:])
        else:
            if len(ev.splitd) > 0:
                nick = ev.splitd[0]
                if tb is False:
                    atr = " ".join(ev.splitd[1:])
                else:
                    restofthestuff = ev.splitd[1]
                    atr = " ".join(ev.splitd[2:])
            else:
                nick = ev.source
                if tb is False:
                    atr = " ".join(ev.splitd[0:])
                else:
                    restofthestuff = ev.splitd[0]
                    atr = " ".join(ev.splitd[1:])

            chan = ev.target
        return (nick, chan, atr, restofthestuff)

    def op(self, bot, cli, ev):
        x = self._getchannick(ev)
        cli.mode(x[1], "+o " + x[0])

    def deop_p(self, bot, cli, ev):
        return self.op_p(bot, cli, ev)

    def deop(self, bot, cli, ev):
        x = self._getchannick(ev)
        cli.mode(x[1], "-o " + x[0])

    def voice_p(self, bot, cli, ev):
        return self.op_p(bot, cli, ev)

    def voice(self, bot, cli, ev):
        x = self._getchannick(ev)
        cli.mode(x[1], "+v " + x[0])

    def devoice_p(self, bot, cli, ev):
        return self.op_p(bot, cli, ev)

    def devoice(self, bot, cli, ev):
        x = self._getchannick(ev)
        cli.mode(x[1], "-v " + x[0])

    def kick_p(self, bot, cli, ev):
        return self.op_p(bot, cli, ev)

    def kick(self, bot, cli, ev):
        x = self._getchannick(ev)
        cli.kick(x[1], x[0], x[2])

    def kickban_p(self, bot, cli, ev):
        return self.op_p(bot, cli, ev)

    def kickban(self, bot, cli, ev):
        x = self._getchannick(ev)
        self.actn = "ban"
        self.nick = x[0]
        self.msg = x[2]
        self.chan = x[1]
        cli.who(self.nick)
        pass

    def timedban_p(self, bot, cli, ev):
        return self.op_p(bot, cli, ev)

    def timedban(self, bot, cli, ev):
        x = self._getchannick(ev, True)
        self.actn = "tban"
        self.nick = x[0]
        self.msg = x[2]
        self.chan = x[1]
        self.t = int(x[3])
        cli.who(self.nick)
        pass

    def unban_p(self, bot, cli, ev):
        return self.op_p(bot, cli, ev)

    def unban(self, bot, cli, ev):
        x = self._getchannick(ev)
        self.actn = "unban"
        self.nick = x[0]
        self.chan = x[1]
        # cli.mode(x[1], "b")
        cli.who(self.nick)

    def topic_p(self, bot, cli, ev):
        return self.op_p(bot, cli, ev)

    def topic(self, bot, cli, ev):
        x = self._getchannick(ev)
        cli.topic(x[1], x[0] + " " + x[2])

    def inmucheck(self, core, cli, nick, channel):
        setting = core.readConf("channel.immunity", channel, "")
        if setting == "":
            return False  # Nadie es inmune :D
        if setting == "voice" and cli.channels[channel].getuser(nick) \
                                                        .isVoiced(True):
            return True
        if setting == "op" and cli.channels[channel].getuser(nick).is_op:
            return True
        return False

    def whoban(self, cli, ev):
        if self.actn is False:
            return
        try:
            if self.inmucheck(self.core, cli, self.nick, self.chan):
                if self.actn != "unban":
                    self.actn = False
                    return
        except:
            pass
        if self.actn == "ban" and self.nick == ev.arguments[4]:
            cli.mode(self.chan, "+b *!*@" + ev.arguments[2])
            cli.kick(self.chan, self.nick, self.msg)
            self.actn = False
        elif self.actn == "tban" and self.nick == ev.arguments[4]:
            cli.mode(self.chan, "+b *!*@" + ev.arguments[2])
            cli.kick(self.chan, self.nick, self.msg)
            self.actn = False
            time.sleep(self.t * 60)
            cli.mode(self.chan, "-b *!*@" + ev.arguments[2])
        elif self.actn == "unban" and self.nick == ev.arguments[4]:
            masc = ev.arguments[4] + "!" + ev.arguments[1] + "@" + \
             ev.arguments[2]
            for i in cli.channels[self.chan].banlist:
                rgx = i.replace("*", ".*").replace("?", ".?")
                p = re.compile(rgx, re.IGNORECASE)
                if p.match(masc):
                    cli.mode(self.chan, "-b " + i)
            self.actn = False
