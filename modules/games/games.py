# -*- coding: utf-8 -*-
from pycobot.pycobot import BaseModel
from peewee.peewee import CharField, IntegerField
import random


class games:

    def __init__(self, core, client):
        # Nos fijamos si somos el único (o el primer) m_games que se cargo.
        # Si es así, entonces cargamos los timehandlers
        l = False
        for k in core.botcli.bots:
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
        core.addCommandHandler("congelar", self, cpriv=5,
        chelp="Congela una cuenta del juego. Sintaxis: congelar <nick> [hiper]")
        core.addCommandHandler("descongelar", self, cpriv=5,
        chelp="Descongela una cuenta del juego. Sintaxis: descongelar <nick>")

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

    def congelar(self, bot, cli, ev, des=False):
        if len(ev.splitd) > 0:
            cli.privmsg(ev.target, "\00304Error\003: Faltan parametros.")
            return 1
        user = GameUser.get(GameUser.nick == ev.splitd[0])
        if user is False:
            self.msg(ev, "El usuario \2%s\2 no existe." % ev.splitd[0], True)
            return 1
        if des is False:
            if len(ev.splitd) < 1 and ev.splitd[1] == "hiper":
                if user.congelado != 2:
                    user.congelado = 2
                else:
                    self.msg("El usuario ya está congelado.", True)
                    return 1
            else:
                if user.congelado != 1:
                    user.congelado = 1
                else:
                    self.msg("El usuario ya está congelado.", True)
                    return 1
        else:
            if user.congelado != 0:
                user.congelado = 0
            else:
                self.msg("El usuario no está congelado.", True)
                return 1
        user.save()

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
            if u.congelado == 1:
                self.msg(ev, "No puedes jugar, esta cuenta ha sido congelada "
                "por un administrador", True)
                return 3  # "Esta cuenta esta congelada"
            elif u.congelado == 2:
                return 4  # "Esta cuenta esta hipercongelada"

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
        elif com == "tragamonedas" or com == "tragaperras":
            self.tragamonedas(u, cli, ev)
        elif com == "rueda":
            self.rueda(u, cli, ev)

    def alta(self, cli, ev):
        ch = GameBank.get(GameBank.bid == 1)
        ul = GameUser.get(GameUser.nick == ev.source)
        if not ul is False:
            self.msg(ev, "Ya estás dado de alta!", True)
        if ch.dinero < 5000:
            self.msg(ev, "El banco está en quiebra, no puedes jugar.",
                True)
        else:
            GameUser.create(nick=ev.source, congelado=0, deuda=0, extrainf=
                "{}", nivel=0, dinero=0)
            u = GameUser.get(GameUser.nick == ev.source)
            self.moneyOp(u, 100, True)
            self.msg(ev, "\2Te has dado de alta!!\2 ahora tienes \2$100"
                "\2 para empezar a jugar!")

    def dinero(self, usr, cli, ev):
        if len(ev.splitd) == 0:
            user = GameUser.get(GameUser.nick == ev.source)
        elif ev.splitd[0] == "banco":
            user = False
            bank = GameBank.get(GameBank.bid == 1)
            resp = ("En el banco hay $\2{0:,}\2. Flags: [\002\00302B\003\002"
            "] [\2Pozo\2 %s]".format(bank.dinero) % bank.pozo)
        else:
            user = usr

        if not user is False:
            resp = "En la cuenta de \2%s\2 hay $\2{0:,}\2. Flags: " \
                " [\2Lvl\2 %s] ".format(user.dinero) % (user.nick, user.nivel)
        self.msg(ev, resp)

    def dados(self, user, cli, ev):
        bank = GameBank.get(GameBank.bid == 1)
        if bank.dinero < 5000:
            self.msg(ev, "El banco está en quiebra, no puedes jugar.",
                True)
            return 1
        if user.dinero < 5:
            self.msg(ev, "No tienes suficiente dinero como para jugar a este."
                "juego. Necesitas $\0025\2 y tienes %s" % user.dinero, True)
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        d3 = random.randint(1, 6)

        d = d1 + d2 + d3
        r = ("\2%s\2: [\2%s+%s+%s=%s\2]" % (ev.source, d1, d2, d3, d))
        if d % 2 == 0:
            w = random.randint(3, 30)
            self.moneyOp(user, w, True)
            self.msg(ev, "%s ganaste $\2%s\2!!" % (r, w))
        else:
            w = random.randint(3, 16)
            self.moneyOp(user, w, False)
            self.msg(ev, "%s perdiste $\2%s\2!!" % (r, w))

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
        self.msg(ev, "\2%s\2: Ahora eres nivel \2%s\2!!" % (user.nick,
             user.nivel))

    def top(self, cli, ev, cant, column="dinero"):
        users = GameUser.select().where(GameUser.congelado == 0)
        c = getattr(GameUser, column)
        users = users.order_by(c.desc()).limit(cant)
        self.msg(ev, "\00306    NICK                NIVEL  DINERO")
        i = 1
        for user in users:
            k = str(i) + "."
            din = "{0:,}".format(user.dinero)
            self.msg(ev, "\2%s\2%s%s%s" % (k.ljust(4), user.nick.ljust(20),
                str(user.nivel).ljust(7), din))
            i = i + 1

    def tragamonedas(self, user, cli, ev):
        bank = GameBank.get(GameBank.bid == 1)
        if bank.dinero < 5000:
            self.msg(ev, "El banco está en quiebra, no puedes jugar.",
                True)
            return 1
        if user.dinero < 15:
            self.msg(ev, "No tienes suficiente dinero como para jugar a este."
                "juego. Necesitas $\00215\2 y tienes %s" % user.dinero, True)
        if user.nivel == 0:
            self.msg(ev, "Debes ser nivel 1 para poder usar este juego", True)

        s = random.randint(6 * user.nivel, 12 * user.nivel)
        p = random.randint(5 * user.nivel, 16 * user.nivel)
        n = random.randint(-9 * user.nivel, 15)
        m = random.randint(12 * user.nivel, 30 * user.nivel)
        e = random.randint(-17 * user.nivel, 3 * user.nivel)
        b = random.randint(-26 * user.nivel, -8 * user.nivel)
        x = random.randint(-17 * user.nivel, 17)
        a = random.randint(8 * user.nivel, 15 * user.nivel)
        nx = []
        nx.append(random.randint(1, 8))
        nx.append(random.randint(1, 8))
        nx.append(random.randint(1, 8))
        comb = ""
        tot = 0

        for n in nx:
            if n == 1:
                comb = comb + "[\2\00303$\003\2]"
                tot += s
            elif n == 2:
                comb = comb + "[\002\00302%\003\002]"
                tot += p
            elif n == 3:
                comb = comb + "[\002\00307#\003\002]"
                tot += n
            elif n == 4:
                comb = comb + "[\002\00309+\003\002]"
                tot += m
            elif n == 5:
                comb = comb + "[\002\00315-\003\002]"
                tot += e
            elif n == 6:
                comb = comb + "[\002\00311/\003\002]"
                tot += b
            elif n == 7:
                comb = comb + "[\002\00313X\003\002]"
                tot += x
            elif n == 8:
                comb = comb + "[\002\00312&\003\002]"
                tot += a
        r = "\2%s\2: %s " % (user.nick, comb)
        if nx[1] == nx[2] and nx[2] == nx[3]:
            tot = 200 * user.nivel
        if tot < 0:
            self.moneyOp(user, tot)
            r += "\2PERDISTE\2"
        else:
            self.moneyOp(user, tot, True)
            r += "\2GANASTE\2"
        r += " $%s" % abs(tot)
        self.msg(ev, r)

    def rueda(self, user, cli, ev):
        banco = GameBank.get(GameBank.bid == 1)
        if banco.pozo < 50000:
            self.msg(ev, "El pozo debe tener por lo menos $50.000 para poder"
                " usar la rueda", True)
            return 1
        if user.dinero < 1000:
            self.msg(ev, "No tienes suficiente dinero como para jugar a este."
                "juego. Necesitas $\0021000\2 y tienes %s" % user.dinero, True)
        if user.nivel >= 4:
            self.msg(ev, "Debes ser nivel 4 para poder usar este juego", True)

        d1 = random.randint(1, 6)
        final = user.dinero
        finalb = banco.dinero
        finalp = banco.pozo
        r = "\2%s\2: " % user.nick
        if d1 == 1:
            final = user.dinero + (banco.pozo * 50 / 100)
            finalp = (banco.pozo * 50 / 100)
            r = "\00304GANASTE\00311 EL 50% DEL DINERO DEL POZO!!!\003"
            r += " Ahora tienes \00303\2$%s" % final
        elif d1 == 2:
            final = user.dinero + (banco.pozo * 25 / 100)
            finalp = (banco.pozo * 75 / 100)
            r = "\00304GANASTE\00311 EL 25% DEL DINERO DEL POZO!!!\003"
            r += " Ahora tienes \00303\2$%s" % final
        elif d1 == 3:
            r = "No pierdes ni ganas nada de dinero."
        elif d1 == 4:
            final = (user.dinero * 25 / 100)
            finalp += (user.dinero * 25 / 100)
            finalb += (user.dinero * 50 / 100)
            r = "\00304PERDISTE\00311 EL 75% DE TU DINERO!\003"
            r += " Ahora tienes \00303\2$%s" % final
        elif d1 == 5:
            final = (user.dinero * 50 / 100)
            finalp += (user.dinero * 25 / 100)
            finalb += (user.dinero * 25 / 100)
            r = "\00304PERDISTE\00311 EL 50% DE TU DINERO!\003"
            r += " Ahora tienes \00303\2$%s" % final
        elif d1 == 6:
            final = 300
            finalp += (user.dinero * 50 / 100)
            finalb += (user.dinero * 50 / 100) - 300
            r = "\00304PERDISTE\00311 TODO TU DINERO!!\003 Tienes $300 para" \
                " amortizar la perdida."

        # No usamos self.moneyOp por que me da pereza!
        user.dinero = final
        banco.dinero = finalb
        banco.pozo = finalp
        user.save()
        banco.save()
        self.msg(ev, r)

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