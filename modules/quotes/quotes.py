# -*- coding: utf-8 -*-
from pycobot.pycobot import BaseModel
from pycobot.tables import User
from peewee.peewee import CharField, IntegerField
import time
import random


class quotes:
    def __init__(self, core, client):
        try:
            tquote.create_table(True)
        except:
            pass
        core.addCommandHandler("quote", self,
        chelp="Maneja los quotes. Sintaxis: quote add <quote>, quote del"
        " <numero>, quote <numero>, quote random.")

    def quote(self, bot, cli, ev):
        if len(ev.splitd) < 1:
            cli.msg(ev.target, "\00304Error\003: Faltan parametros.")
            return 1

        if ev.splitd[0] == "add":
            if len(ev.splitd) < 2:
                cli.msg(ev.target, "\00304Error\003: Faltan parametros.")
                return 1
            try:
                uid = bot.authd[ev.source2]
            except:
                cli.msg(ev.target, "\00304Error\003: Debes estar identific"
                    "ado con el bot para añadir quotes!")
                return 1
            u = User.get(User.uid == uid)
            if u is False:
                cli.msg(ev.target, "\00304Error\003: Debes estar identific"
                    "ado con el bot para añadir quotes!")
                return 1
            ptime = time.time()
            user = u.name
            quote = " ".join(ev.splitd[1:])
            tquote.create(channel=ev.target, nick=user, ts=ptime, quote=quote)
            cli.msg(ev.target, "Quote añadido.")
        elif ev.splitd[0] == "del":
            if len(ev.splitd) < 2:
                cli.msg(ev.target, "\00304Error\003: Faltan parametros.")
                return 1
            if self.is_numeric(ev.splitd[1]) is False:
                cli.msg(ev.target, "\00304Error\003: Faltan parametros.")
                return 1
            try:
                uid = bot.authd[ev.source2]
            except:
                cli.msg(ev.target, "\00304Error\003: Debes estar identific"
                    "ado con el bot para añadir quotes!")
                return 1
            usr = User.get(User.uid == uid)
            quoteid = ev.splitd[1]
            u = tquote.get(tquote.qid == quoteid)
            if u.nick == usr.name:
                u.delete_instance()
                cli.msg(ev.target, "Se ha eliminado el quote")
            else:
                if bot.authchk(ev.source2, 5, "quotes"):
                    u.delete_instance()
                    cli.msg(ev.target, "Se ha eliminado el quote")
                else:
                    cli.msg(ev.target, "\00304Error\003: No autorizado")

        elif ev.splitd[0] == "random":
            q = tquote.select().where(tquote.channel == ev.target)
            qc = tquote.select().where(tquote.channel == ev.target).count()
            if qc == 0:
                cli.msg(ev.target, "\00304Error\003: No hay quotes en"
                    " este canal.")
                return 1
            u = q[random.randint(0, qc - 1)]
            tm = time.asctime(time.localtime(float(u.ts)))
            cli.msg(ev.target, "Quote \2%s\2 por \2%s\2, añadido el"
                " \2%s\2: %s" % (u.qid, u.nick, tm, u.quote))
        else:
            if self.is_numeric(ev.splitd[0]) is False:
                cli.msg(ev.target, "\00304Error\003: Faltan parametros.")
                return 1
            quoteid = ev.splitd[0]
            u = tquote.get(tquote.qid == quoteid)
            if u is False:
                cli.msg(ev.target, "\00304Error\003: Ese quote no existe!")
                return 1
            if u.channel != ev.target:
                cli.msg(ev.target, "\00304Error\003: Quote inválido.")
                return 1
            tm = time.asctime(time.localtime(float(u.ts)))
            cli.msg(ev.target, "Quote \2%s\2 por \2%s\2, añadido el"
                " \2%s\2: %s" % (u.qid, u.nick, tm, u.quote))

    def is_numeric(self, var):
        try:
            float(var)
            return True
        except ValueError:
            return False


class tquote(BaseModel):
    qid = IntegerField(primary_key=True)
    quote = CharField()
    channel = CharField()
    ts = CharField()
    nick = CharField()

    class Meta:
        db_table = "quotes"
