# -*- coding: utf-8 -*-
import irc.client


class op:
    def __init__(self, core, client):
        core.addCommandHandler("op", self, cpriv=5, cprivchan=True, chelp=
        "Da op en un canal. Sintaxis: op [canal] [nick]")
        core.addCommandHandler("deop", self, cpriv=5, cprivchan=True, chelp=
        "Quita op en un canal. Sintaxis: deop [canal] [nick]")
        core.addCommandHandler("voice", self, cpriv=5, cprivchan=True, chelp=
        "Da voz en un canal. Sintaxis: voice [canal] [nick]")
        core.addCommandHandler("devoice", self, cpriv=5, cprivchan=True, chelp=
        "Quita voz en un canal. Sintaxis: devoice [canal] [nick]")
        core.addCommandHandler("kick", self, cpriv=5, cprivchan=True, chelp=
        "Expusa a alguien de un canal. Sintaxis: kick [canal] [nick]")
        core.addCommandHandler("kickban", self, cpriv=5, cprivchan=True, chelp=
        "Banea a alguien de un canal. Sintaxis: kickban [canal] [nick]")
        core.addCommandHandler("unban", self, cpriv=5, cprivchan=True, chelp=
        "Des-banea a alguien de un canal. Sintaxis: unban [canal] [nick]")
        core.addCommandHandler("topic", self, cpriv=5, cprivchan=True, chelp=
        "Cambia el topic de un canal. Sintaxis: topic [canal] [topic]")

        core.addHandler("whoreply", self, "whoban")

    def op_p(self, bot, cli, ev):
        if len(ev.splitd) > 0 and irc.client.is_channel(ev.splitd[0]):
            return ev.splitd[0]
        else:
            return ev.target

    def _getchannick(self, ev):
        if len(ev.splitd) > 0 and irc.client.is_channel(ev.splitd[0]):
            chan = ev.splitd[0]
            if len(ev.splitd) > 1:
                nick = ev.splitd[1]
                atr = " ".join(ev.splitd[2:])
            else:
                nick = ev.source
                atr = " ".join(ev.splitd[1:])
        else:
            if len(ev.splitd) > 0:
                nick = ev.splitd[0]
                atr = " ".join(ev.splitd[1:])
            else:
                nick = ev.source
                atr = " ".join(ev.splitd[0:])

            chan = ev.target
        return (nick, chan, atr)

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

    def unban_p(self, bot, cli, ev):
        return self.op_p(bot, cli, ev)

    def unban(self, bot, cli, ev):
        pass

    def topic_p(self, bot, cli, ev):
        return self.op_p(bot, cli, ev)

    def topic(self, bot, cli, ev):
        x = self._getchannick(ev)
        cli.topic(x[1], x[0] + " " + x[2])

    def whoban(self, cli, ev):
        if self.actn == "ban" and self.nick == ev.arguments[4]:
            cli.mode(self.chan, "+b *!*@" + ev.arguments[2])
            cli.kick(self.chan, self.nick, self.msg)
