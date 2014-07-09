# -*- coding: utf-8 -*-

from pycobot.pycobot import BaseModel
from peewee.peewee import CharField, IntegerField
from irc import client
import time


class antiflood:
    def __init__(self, core, client):
        self.users = {}
        self.bans = {}
        self.chans = {}
        try:
            AntiFloodChan.create_table()
        except:
            pass
        core.addCommandHandler("antiflood", self, cpriv=7, chelp=
        "Maneja el antiflood de un canal. Sintaxis: antiflood <canal> <on/off>"
        " [mensajes] [segundos]", cprivchan=True)
        core.addHandler("pubmsg", self, "pubmsghandle")
        self.updatechancache()
        self.core = core

    def updatechancache(self):
        self.chans = {}
        u = AntiFloodChan.select()
        for x in u:
            self.chans[x.chan] = {}
            self.chans[x.chan]['sec'] = x.ratesec
            self.chans[x.chan]['msg'] = x.ratemsg

    def pubmsghandle(self, cli, ev):
        source = ev.source2
        try:
            self.chans[ev.target]
        except:
            return 0
        try:
            try:
                self.users[ev.target]
            except KeyError:
                self.users[ev.target] = {}

            self.users[ev.target][client.parse_nick(source)[4]]
        except KeyError:
            self.users[ev.target][client.parse_nick(source)[4]] = {}
            self.users[ev.target][client.parse_nick(source)[4]]['kicked'] = False
            self.users[ev.target][client.parse_nick(source)[4]]['firstmsg'] = 0
            self.users[ev.target][client.parse_nick(source)[4]]['msgcount'] = 0

        if self.users[ev.target][client.parse_nick(source)[4]]['firstmsg'] == 0:
            self.users[ev.target][client.parse_nick(source)[4]]['firstmsg'] = time.time()
            self.users[ev.target][client.parse_nick(source)[4]]['msgcount'] += 1
        else:
            if (time.time() - self.users[ev.target][client.parse_nick(source)[4]]['firstmsg']) >= self.chans[ev.target]['sec']:
                self.users[ev.target][client.parse_nick(source)[4]]['firstmsg'] = 0
                self.users[ev.target][client.parse_nick(source)[4]]['msgcount'] = 0
            else:
                if self.users[ev.target][client.parse_nick(source)[4]]['msgcount'] >= self.chans[ev.target]['msg']:
                    self.users[ev.target][client.parse_nick(source)[4]]['firstmsg'] = 0
                    self.users[ev.target][client.parse_nick(source)[4]]['msgcount'] = 0
                    self.floodkick(cli, ev.target, ev.source, ev.source2)
                self.users[ev.target][client.parse_nick(source)[4]]['msgcount'] += 1
    
    def inmucheck(self, core, cli, nick, channel):
        setting = core.readConf("channel", channel, "")
        if setting == "":
            return False  # Nadie es inmune :D
        if setting == "voice" and cli.channels[channel].getuser(nick).isVoiced(True):
            return True
        if setting == "op" and cli.channels[channel].getuser(nick).is_op:
            return True
        return False

    def floodkick(self, cli, chan, nick, source):
        if self.inmucheck(self.core, cli, nick, chan):
            return
        if self.users[chan][client.parse_nick(source)[4]]['kicked'] is False:
            self.users[chan][client.parse_nick(source)[4]]['kicked'] = True
            cli.kick(chan, nick, "No hagas flood.")
        else:
            cli.mode(chan, "+b *!*@" + client.parse_nick(source)[4])
            cli.kick(chan, nick, "No hagas flood.")
            time.sleep(900)
            cli.mode(chan, "-b *!*@" + client.parse_nick(source)[4])

    def antiflood_p(self, bot, cli, ev):
        if len(ev.splitd) > 2:
            return ev.splitd[0]
        else:
            return 0

    def antiflood(self, bot, cli, ev):
        if not len(ev.splitd) > 1:
            cli.msg(ev.target, "\00304Error\003: Faltan parametros.")
            return 0
        ul = AntiFloodChan.get(AntiFloodChan.chan == ev.splitd[0])
        if ev.splitd[1] == "on":
            if not len(ev.splitd) > 3:
                cli.msg(ev.target, "\00304Error\003: Faltan parametros.")
                return 0
            if not ul is False:
                ul.ratesec = ev.splitd[3]
                ul.ratemsg = ev.splitd[2]
                ul.save()
            else:
                AntiFloodChan.create(chan=ev.splitd[0], ratesec=ev.splitd[3],
                                                         ratemsg=ev.splitd[2])
            cli.msg(ev.target, "Se ha activado el antiflood en \2{0}\2"
                                                        .format(ev.splitd[0]))
        elif ev.splitd[1] == "off":
            if ul is False:
                cli.msg(ev.target, "\00304Error\003: El antiflood no esta"
                                                    " activado en ese canal.")
            else:
                ul.delete_instance()
                cli.msg(ev.target, "Se ha desactivado el antiflood en "
                                                "\2{0}\2".format(ev.splitd[0]))
        self.updatechancache()


class AntiFloodChan(BaseModel):
    cid = IntegerField(primary_key=True)
    chan = CharField()
    ratesec = IntegerField()
    ratemsg = IntegerField()
