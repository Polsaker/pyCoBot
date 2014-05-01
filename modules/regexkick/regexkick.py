# -*- coding: utf-8 -*-
from pycobot.pycobot import BaseModel
from peewee.peewee import CharField, IntegerField
import re


class regexkick:

    def __init__(self, core, client):
        self.chancache = {}
        core.addCommandHandler("regexkick", self, cpriv=7, cprivchan=True,
         chelp=
        "Maneja los kicks por expresiones regulares. Sintaxis: regexkick add "
        "<canal> <regex>; regexkick list <canal>; regexlist del <id>")
        try:
            regexKick.create_table(True)
        except:
            pass
        core.addHandler("pubmsg", self, "msghandler")
        self.updatechancache()

    def msghandler(self, cli, ev):
        try:
            for x in self.chancache[ev.target.lower()]:
                l = re.compile(x, re.IGNORECASE)
                u = l.match(ev.arguments[0])
                if u is not None:
                    cli.kick(ev.target, ev.source, "")
        except KeyError:
            pass

    def updatechancache(self):
        self.chancache = {}
        u = regexKick.select()

        for x in u:
            try:
                self.chancache[x.channel].append(x.regex)
            except KeyError:
                self.chancache[x.channel] = []
                self.chancache[x.channel].append(x.regex)

    def regexkick_p(self, bot, cli, ev):
        if len(ev.splitd) < 2:
            cli.notice(ev.target, "Faltan parámetros")
            return 0
        if ev.splitd[0] == "add" or ev.splitd[0] == "list":
            return ev.splitd[1]
        elif ev.splitd[0] == "del":
            ul = regexKick.get(regexKick.rid == ev.arguments[1])
            if ul is not False:
                return ul.channel

    def regexkick(self, bot, cli, ev):
        if len(ev.splitd) < 1:
            return 0

        if ev.splitd[0] == "add":
            regexKick.create(channel=ev.splitd[1].lower(),
                            regex=" ".join(ev.splitd[2:]))
            cli.notice(ev.target, "Se ha añadido el akick.")
        elif ev.splitd[0] == "list":
            u = regexKick.select().where(regexKick.channel ==
                                                        ev.splitd[1].lower())
            for x in u:
                cli.notice(ev.target, "\2{0}\2 - {1}".format(x.rid, x.regex))
        elif ev.splitd[0] == "del":
            ul = regexKick.get(regexKick.rid == ev.arguments[1])
            ul.delete_instance()
            cli.notice(ev.target, "Se ha eliminado el akick.")
        self.updatetechancache()


class regexKick(BaseModel):
    rid = IntegerField(primary_key=True)
    channel = CharField()
    regex = CharField()