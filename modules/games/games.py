# -*- coding: utf-8 -*-
from pycobot.pycobot import BaseModel
from peewee.peewee import CharField, IntegerField
import random
import copy


class games:

    def __init__(self, core, client):
        # Nos fijamos si somos el único (o el primer) m_games que se cargo.
        # Si es así, entonces cargamos los timehandlers
        self.rbal = random.randint(0, 5)
        self.rcnt = 0
        self.timehandlers = ""
        l = False
        for k in core.botcli.bots:
            if k.is_loaded("games") is True:
                if k.getmodule("games").timehandlers == k.getmodule("games"):
                    self.timehandlers = k.getmodule("games")
                l = True
        self.cli = client
        self.core = core
        if l is False:
            self.timehandlers = self
            core.addTimeHandler(1800, self, "th30min")
            self.lastuser = False
        try:
            GameChannel.create_table(True)
            GameBank.create_table(True)
            GameUser.create_table(True)
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
        core.addCommandHandler("changemoney", self, cpriv=6,
        chelp="Cambia la cantidad de dinero almacenado en una cuenta. Sintaxis"
        ": changemoney <nick> <dinero>")

    ## Comandos
    def changemoney(self, bot, cli, event):
        if len(event.splitd) < 2:
            self.msg(event, "Faltan parametros", True)
        if event.splitd[0] == "banco":
            user = GameBank.get(GameBank.bid == 1)
        else:
            user = GameUser.get(GameUser.nick == event.splitd[0])
        user.dinero = event.splitd[1]
        user.save()

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
            cli.msg(ev.target, "\00304Error\003: Faltan parametros.")
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

    def descongelar(self, bot, cli, ev):
        self.congelar(bot, cli, ev, True)

    def congelar(self, bot, cli, ev, des=False):
        if len(ev.splitd) < 1:
            cli.msg(ev.target, "\00304Error\003: Faltan parametros.")
            return 1
        user = GameUser.get(GameUser.nick == ev.splitd[0])
        if user is False:
            self.msg(ev, "El usuario \2%s\2 no existe." % ev.splitd[0], True)
            return 1
        if des is False:
            if len(ev.splitd) < 1 and ev.splitd[1] == "hiper":
                if user.congelado != 2:
                    user.congelado = 2
                    self.msg(ev, "Se ha congelado a \2%s\2" % user.nick)
                else:
                    self.msg(ev, "El usuario ya está congelado.", True)
                    return 1
            else:
                if user.congelado != 1:
                    user.congelado = 1
                    self.msg(ev, "Se ha congelado a \2%s\2" % user.nick)
                else:
                    self.msg(ev, "El usuario ya está congelado.", True)
                    return 1
        else:
            if user.congelado != 0:
                user.congelado = 0
                self.msg(ev, "Se ha descongelado a \2%s\2" % user.nick)
            else:
                self.msg(ev, "El usuario no está congelado.", True)
                return 1
        user.save()

    ## /Comandos

    ## Timehandler!
    def th30min(self, bot, cli):
        bank = GameBank.get(GameBank.bid == 1)
        bank.dinero += 25
        bank.save()
        users = GameUser.select()
        for user in users:
            user.deuda += (user.deuda * 5 / 100)
            user.save()

        if self.lastuser is not False:
            user = GameUser.get(GameUser.nick == self.lastuser)
            l = random.randint(1, 10)
            if l == 1:
                self.moneyOp(user, (user.dinero * 5 / 100))
                t = ("\2%s\2 ha caido ebrio/a en el suelo. Alguien se aprovecha"
                    " y le roba algo de dinero, le quedan $\2%s\2." % (
                        self.lastuser, user.dinero))
            elif l == 2:
                self.moneyOp(user, (user.dinero * 5 / 100), True)
                t = ("\2%s\2 ha encontrado una billetera en el suelo. Tira la"
                "billetera y se queda con el dinero. Ahora tiene $\2%s\2." % (
                        self.lastuser, user.dinero))
            elif l == 3:
                self.moneyOp(user, (user.dinero * 5 / 100))
                t = ("A \2%s\2 le ha caido un rayo aún estando dentro del casi"
                "no! Este extraño suceso hace que parte de su dinero se queme."
                " Le quedan $\2%s\2." % (self.lastuser, user.dinero))
            elif l == 4:
                self.moneyOp(user, (user.dinero * 5 / 100))
                t = ("\2%s\2 es estafado con el típico mail del principe niger"
                "iano que necesita dinero para huir."
                " Le quedan $\2%s\2." % (self.lastuser, user.dinero))
            elif l == 5:
                self.moneyOp(user, (user.dinero * 5 / 100))
                t = ("A \2%s\2 se le cae algo de dinero por el retrete."
                " Le quedan $\2%s\2." % (self.lastuser, user.dinero))
            elif l == 6:
                self.moneyOp(user, (user.dinero * 8 / 100))
                t = ("\2%s\2 pierde algo de dinero invirtiendo en bitcoins"
                " Le quedan $\2%s\2." % (self.lastuser, user.dinero))
            elif l == 7:
                self.moneyOp(user, (user.dinero * 5 / 100), True)
                t = ("\2%s\2 ha encontrado algo de dinero en la billetera"
                " de la persona que acaba de asesinar en el tren."
                " Ahora tiene $\2%s\2." % (self.lastuser, user.dinero))
            elif l == 8:
                self.moneyOp(user, (user.dinero * 7 / 100))
                t = ("\2%s\2 es abducido por unos extraterrestres. No son tont"
                "os, se han llevado una parte de su dinero..."
                " Ahora tiene $\2%s\2." % (self.lastuser, user.dinero))
            elif l == 9:
                self.moneyOp(user, (user.dinero * 7 / 100), True)
                t = ("\2%s\2 encuentra algo de dinero en esa caja fuerte que "
                "acaba de romper."
                " Ahora tiene $\2%s\2." % (self.lastuser, user.dinero))
            elif l == 10:
                self.moneyOp(user, (user.dinero * 7 / 100))
                t = ("A \2%s\2 lo sacan del casino por que su mugre atrae a la"
                "s moscas. Se toma un baño, le paga a los guardias y continua "
                "jugando. Ahora tiene $\2%s\2." % (self.lastuser, user.dinero))
            self.gmsg(t)

            self.lastuser = False
    ## /Timehandler

    def commandhandle(self, cli, event):
        ev = copy.deepcopy(event)
        if not ev.arguments[0][0] == "!":
            return 0
        c = GameChannel.get(GameChannel.channel == ev.target)
        if c is False:
            return 1  # "Los juegos no están habilitados en este canal.."
        com = ev.arguments[0][1:].split(" ")[0]
        try:
            if ev.splitd[0][0] == "!":
                del ev.splitd[0][0]
        except:
            pass
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
        print(com)
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
        elif com == "circulando":
            self.circulando(cli, ev)
        elif com == "lvlp":
            self.lvlp(cli, ev)
        elif com == "prestamo":
            self.prestamo(u, cli, ev)
        elif com == "ruleta":
            self.ruleta(cli, ev)

    def alta(self, cli, ev):
        ch = GameBank.get(GameBank.bid == 1)
        ul = GameUser.get(GameUser.nick == ev.source)
        if not ul is False:
            self.msg(ev, "Ya estás dado de alta!", True)
            return 1
        if ch.dinero < 5000:
            self.msg(ev, "El banco está en quiebra, no puedes jugar.",
                True)
            return 1
        else:
            GameUser.create(nick=ev.source, congelado=0, deuda=0, extrainf=
                "{}", nivel=0, dinero=0)
            u = GameUser.get(GameUser.nick == ev.source)
            self.moneyOp(u, 100, True)
            self.msg(ev, "\2Te has dado de alta!!\2 ahora tienes \2$100"
                "\2 para empezar a jugar!")

    def dinero(self, usr, cli, ev):
        if len(ev.splitd) >= 1:
            user = ev.source
        else:
            user = ev.splitd[1]
        if ev.splitd[0] == "banco":
            user = False
            bank = GameBank.get(GameBank.bid == 1)
            resp = ("En el banco hay $\2{0:,}\2. Flags: [\002\00302B\003\002"
            "] [\2Pozo\2 %s]".format(bank.dinero) % bank.pozo)
            self.msg(ev, resp)
            return 1
        else:
            user = GameUser.get(GameUser.nick == user)

        resp = "En la cuenta de \2%s\2 hay $\2{0:,}\2. Flags: " \
            " [\2Lvl\2 %s] ".format(user.dinero) % (user.nick, user.nivel)
        if user.deuda != 0:
            resp += "[\2Deuda\2 {0}] ".format(user.deuda)
        if user.congelado != 0:
            resp += "[\2\00304F\2\3] "
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
            return 1

        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        d3 = random.randint(1, 6)
        if user.nivel > 2:
            self.timehandlers.lastuser = user.nick
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
            return 1
        if user.nivel == 0:
            self.msg(ev, "Debes ser nivel 1 para poder usar este juego", True)
            return 1
        if user.nivel > 2:
            self.timehandlers.lastuser = user.nick
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
        if nx[0] == nx[1] and nx[1] == nx[2]:
            tot = 200 * user.nivel
        if tot < 0:
            self.moneyOp(user, abs(tot))
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
            return 1
        if user.nivel < 4:
            self.msg(ev, "Debes ser nivel 4 para poder usar este juego", True)
            return 1
        self.timehandlers.lastuser = user.nick
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
        self.msg(ev, user.nick + ": " + r)

    def circulando(self, cli, ev):
        banco = GameBank.get(GameBank.bid == 1)
        users = GameUser.select()
        tot = 0
        totc = 0
        totu = 0
        tot += banco.dinero
        tot += banco.pozo

        for user in users:
            tot += user.dinero
            totu += user.dinero
            if user.congelado != 0:
                totc += user.dinero
        r = "En total hay circulando $\2{0:,}\2 ($\2{1:,}\2 en el banco, " \
            "$\2{2:,}\2 en el pozo, $\2{3:,}\2 en manos de los usuarios y " \
            "$\2{4:,}\2 fuera de circulación en cuentas congeladas)".format(
            tot, banco.dinero, banco.pozo, totu, totc)
        self.msg(ev, r)

    def lvlp(self, cli, ev):
        if len(ev.splitd) == 0:
            self.msg(ev, "Faltan parámetros", True)
            return 1
        if int(ev.splitd[0]) > 3000:
            self.msg(ev, "Digamos que niveles por encima de este no existen..",
                True)
            return 1
        i = 0
        cost = 125
        while i != int(ev.splitd[0]):
            cost = cost * 2
            i = i + 1

        self.msg(ev, "El nivel \2{0}\2 cuesta $\2{1:,}".format(i, cost))

    def ruleta(self, cli, ev):
        if self.rcnt == self.rbal:
            cli.kick(ev.target, ev.source, "*BOOM*")
            self.rcnt = 0
            self.rbal = random.randint(0, 5)
        else:
            cli.msg(ev.target, ev.source + ": *CLICK*")

        if self.rcnt == 5:
            self.rcnt = 0
            self.rbal = random.randint(0, 5)
        else:
            self.rcnt += 1

    def prestamo(self, user, cli, ev):
        i = 0
        tot = 500
        while i != user.nivel:
            tot += tot * 25 / 100
            i += 1
        if user.deuda != 0:
            tot -= user.deuda
        if len(ev.splitd) == 0:
            self.msg(ev, "\2{0}\2: Puedes pedir hasta $\2{1}\2".format(
                user.nick, tot))
        elif ev.splitd[0] == "pagar":
            if user.dinero > user.deuda + 100:
                self.moneyOp(user, user.deuda)
                user.deuda = 0
                self.msg(ev, "Has pagado tu deuda.")
            else:
                tot = user.deuda - (user.dinero - 100)
                self.moneyOp(user, tot)
                user.deuda -= tot
                self.msg(ev, "Has pagado una parte de tu deuda. Todavía debes"
                    " $\2{0}".format(user.deuda))
            user.save()
        else:
            if int(ev.splitd[0]) <= tot:
                user.deuda = int(ev.splitd[0]) + 100
                user.dinero += int(ev.splitd[0])
                user.save()
                self.msg(ev, "El banco te ha otorgado el préstamo.")
            else:
                self.msg(ev, "Solo puedes pedir hasta \2{0}".format(tot))

    # Envía un mensaje al servidor..
    def msg(self, ev, msg, error=False):
        msg = "\x0f" + msg  # >:D
        if error is True:
            msg = "\00304Error\003: " + msg
        self.cli.msg(ev.target, msg)

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

    # Envía un notice a todos los canales con los juegos habilitados
    def gmsg(self, msg):
        chans = GameChannel.select()
        for k in self.core.botcli.bots:
            for chan in chans:
                k.server.notice(chan.channel, msg)
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
