import re
from pycobot.pycobot import BaseModel
from peewee.peewee import CharField, IntegerField
import time


class karma:
    karmare = re.compile(r"^([a-zA-Z0-9\[\]\{\}\\\|\-\_\`^]*)(:?,? ?)?"
                            "(\+\+|\-\-)")

    def __init__(self, core, client):
        Karma.create_table(True)
        core.addCommandHandler("karma", self, chelp="karma.help")
        core.addHandler("pubmsg", self, "karmacount")
        self.lasttime = {}

    def karma(self, bot, cli, ev):
        if ev.type == "privmsg":
            return 1
        if not len(ev.splitd) > 0:
            cli.msg(ev.target, bot._(ev, 'core', "generic.missigparam"))
            return 1
        user = Karma.get(Karma.nick == ev.splitd[0].lower(),
                             Karma.chan == ev.target.lower())
        if user is False:
            cli.msg(ev.target, bot._(ev, self, 'karma.no').format(ev.splitd[0]))
        else:
            cli.msg(ev.target, bot._(ev, self, 'karma.msg').format(
                                            ev.splitd[0], str(user.karma)))

    def karmacount(self, cli, ev):
        l = self.karmare.match(ev.arguments[0])
        if l is not None:
            if l.group(1).lower() == ev.source.lower():
                return 1
            try:
                self.lasttime[ev.target]
            except:
                self.lasttime[ev.target] = {}
            try:
                self.lasttime[ev.target][ev.source]
            except:
                self.lasttime[ev.target][ev.source] = {}
            try:
                if (time.time() -
                self.lasttime[ev.target][ev.source][l.group(1).lower()]) < 900:
                    return 0  # >:D
            except:
                pass

            user = Karma.get(Karma.nick == l.group(1).lower(),
                             Karma.chan == ev.target.lower())
            if user is False:
                Karma.create(nick=l.group(1).lower(), chan=ev.target.lower(),
                            karma=int(0))
                user = Karma.get(Karma.nick == l.group(1).lower(),
                             Karma.chan == ev.target.lower())
            if l.group(3) == "++":
                user.karma += 1
            else:
                user.karma -= 1
            user.save()
            self.lasttime[ev.target][ev.source][l.group(1).lower()] = time.time()


class Karma(BaseModel):
    nick = CharField()
    chan = CharField()
    karma = IntegerField()
