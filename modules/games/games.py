# -*- coding: utf-8 -*-
from pycobot.pycobot import BaseModel
from peewee.peewee import CharField, IntegerField
import random


class games:

    def __init__(self, core, client):
        # Nos fijamos si somos el único (o el primer) m_games que se cargo.
        # Si es así, entonces cargamos los timehandlers
        l = False
        for w, k in enumerate(core.botcli.boservers):
            if k.is_loaded("games") is True:
                l = True
        self.cli = client
        if l is False:
            pass
            #core.addTimeHandler(...)
        try:
            GameChannel.create_table()
            GameBank.create_table()
            GameUser.create_table()
            GameBank.create(bid=1, dinero=100000000, pozo=0, extrainf="{}")
        except:
            pass
        core.addHandler("pubmsg", self, "commandhandle")
        core.addCommandHandler("enablegame", self, cpriv=4, cprivchan=True,
        chelp="Activa los juegos en un canal. Sintaxis: enablegame <canal>")
        core.addCommandHandler("disablegame", self, cpriv=4, cprivchan=True,
        chelp="Desactiva los juegos en un canal. Sintaxis: disablegame <canal>")

    ## Comandos
    def disablegame(self, bot, cli, event):
        return self.enablegame(bot, cli, event, True)

    def disablegame_p(self, bot, cli, event):
        return self.enablegame_p(bot, cli, event)

    def enablegame_p(self, bot, cli, event):
        if len(event.splitd) > 0:
            return event.splitd[0]
        return 1

    def enablegame(self, bot, cli, ev, dis=False):
        if len(ev.splitd) < 1:
            cli.privmsg(ev.target, "\00304Error\003: Faltan parametros.")
            return 1
        c = GameChannel.get(GameChannel.channel == ev.splitd[0])
        if dis is False:
            if c is False:
                GameChannel.create(channel=ev.splitd[0])
                self.msg(ev, "Se han activado los juegos en \2" + ev.splitd[0])
            else:
                self.msg(ev, "Los juegos ya están activados en \2" +
                 ev.splitd[0], True)
        else:
            if c is False:
                self.msg(ev, "Los no están activados en \2" + ev.splitd[0],
                    True)
            else:
                c.delete_instance()
                self.msg(ev, "Se han desactivado los juegos en \2" +
                    ev.splitd[0])
    ## /Comandos

    def commandhandle(self, cli, ev):
        if not ev.splitd[0][0] == "!":
            return 0
        c = GameChannel.get(GameChannel.channel == ev.target)
        if c is False:
            return 1  # "Los juegos no están habilitados en este canal.."
        com = ev.splitd[0][1:]
        del ev.splitd[0]
        if com != "alta":
            u = GameUser.get(GameUser.nick == ev.source)
            if u is False:
                self.msg(ev, "No estás dado de alta en el juego. Para"
                " darte de alta escribe \2!alta\2", True)
                return 2  # "No estás dado de alta en el juego"
        # Comandos....
        if com == "alta":
            self.alta(cli, ev)
        elif com == "dados" or com == "dado":
            self.dados(u, cli, ev)
        elif com == "dinero" or com == "saldo":
            self.dinero(u, cli, ev)
        elif com == "lvlup" or com == "nivel":
            self.lvlup(u, cli, ev)
        elif com == "top":
            self.top(cli, ev, 5)
        elif com == "top10":
            self.top(cli, ev, 10)
        elif com == "lvltop":
            self.top(cli, ev, 5, "nivel")

    def alta(self, cli, ev):
        ch = GameBank.get(GameBank.bid == 1)
        u = GameUser.get(GameUser.nick == ev.source)
        if not u is False:
            self.msg(ev, "Ya estás dado de alta!", True)
        if ch.dinero < 5000:
            self.msg(ev, "El banco está en quiebra, no puedes jugar.",
                True)
        else:
            u = GameUser.create(nick=ev.source, congelado=0, deuda=0, extrainf=
                "{}", nivel=0, dinero=0)
            self.moneyOp(u, 100, True)
            self.msg(ev, "\2Te has dado de alta!!\2 ahora tienes \2$100"
                "\2 para empezar a jugar!")

    def dinero(self, usr, cli, ev):
        if len(ev.splitd) == 0:
            user = GameUser.get(GameUser.nick == ev.source)
        elif ev.splitd[0] == "banco":
            user = False
            bank = GameBank.get(GameBank.bid == 1)
            resp = ("En el banco hay $\2%s\2. Flags: [\002\00302B\003\002"
            "] [\2Pozo\2 %s]" % (bank.dinero, bank.pozo))
        else:
            user = usr

        if not user is False:
            resp = "En la cuenta de \2%s\2 hay $\2%s\2. Flags: [\2Lvl\2 %s] " \
            % (user.nick, user.dinero, user.nivel)
        self.msg(ev, resp)

    def dados(self, user, cli, ev):
        bank = GameBank.get(GameBank.bid == 1)
        if bank.dinero < 5000:
            self.msg(ev, "El banco está en quiebra, no puedes jugar.",
                True)
            return 1
        if user.dinero < 5:
            self.msg(ev, "No tienes suficiente dinero como para jugar a este."
                "juego. Necesitas $\25\2 y tienes %s" % user.dinero, True)
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        d3 = random.randint(1, 6)

        d = d1 + d2 + d3
        r = ("\2%s\2: [\2%s+%s+%s=%s\2]" % (ev.source, d1, d2, d3, d))
        if d % 2 == 0:
            w = random.randint(3, 30)
            self.moneyOp(user, w, True)
            self.msg(ev, "%s ganaste %s!!" % (r, w))
        else:
            w = random.randint(3, 16)
            self.moneyOp(user, w, False)
            self.msg(ev, "%s perdiste %s!!" % (r, w))

    def lvlup(self, user, cli, ev):
        i = 0
        cost = 125  # Costo base para subir de nivel
        while i != user.nivel + 1:
            cost = cost * 2
            i = i + 1

        if user.dinero < (cost + 50):
            self.msg(ev, "Necesitas por lo menos $\2%s\2 para poder pasar al"
                " nivel %s!" % (cost + 50, user.nivel + 1))
            return 1
        self.moneyOp(user, cost)
        user.nivel = user.nivel + 1
        user.save()

    def top(self, cli, ev, cant, column="dinero"):
        users = GameUser.select().where(GameUser.congelado == 0)
        c = getattr(GameUser, column)
        users = users.order_by(c.desc()).limit(cant)
        self.msg(ev, "\00306    NICK                NIVEL  DINERO")
        i = 1
        for user in users:
            k = str(i) + "."
            self.msg(ev, "\2%s\2%s%s%s" % (k.ljust(4), user.nick.ljust(20),
                str(user.nivel).ljust(7), user.dinero))
            i = i + 1

    # Envía un mensaje al servidor..
    def msg(self, ev, msg, error=False):
        msg = "\x0f" + msg  # >:D
        if error is True:
            msg = "\00304Error\003: " + msg
        self.cli.privmsg(ev.target, msg)

    # función para realizar operaciones usuario-banco. Si el parametro "pozo"
    # es True, la mitad del dinero va al pozo y la otra mitad va al banco. Si
    # el parametro "add" es True, da dinero al usuario y quita al banco.
    # Viceversa si add es False.
    def moneyOp(self, user, cant, add=False, pozo=True):
        bank = GameBank.get(GameBank.bid == 1)
        if not user is False:
            if add is False:
                user.dinero = user.dinero - cant
                if pozo is True:
                    cant = cant / 2
                    bank.pozo = bank.pozo + cant
                bank.dinero = bank.dinero + cant
            else:
                user.dinero = user.dinero + cant
                bank.dinero = bank.dinero - cant
            user.save()
            bank.save()
        else:
            return False

# Tablas... (El campo extrainf está reservado para implementar nuevas
# características sin tener que añadir mas campos a las tablas existentes.


class GameUser(BaseModel):
    uid = IntegerField(primary_key=True)
    nick = CharField()
    dinero = IntegerField()
    congelado = IntegerField()
    nivel = IntegerField()
    deuda = IntegerField()
    extrainf = CharField()


class GameChannel(BaseModel):
    cid = IntegerField(primary_key=True)
    channel = CharField()


class GameBank(BaseModel):
    bid = IntegerField(primary_key=True)
    dinero = IntegerField()
    pozo = IntegerField()
    extrainf = CharField()