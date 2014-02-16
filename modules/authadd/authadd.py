# -*- coding: utf-8 -*-
from pycobot.tables import User, UserPriv
import hashlib


class authadd:
    def __init__(self, core, client):
        core.addCommandHandler("register", self, chelp="Registra un usuario con"
        " el bot. Sintaxis: register <usuario> <contraseña> USAR SOLO EN MENSAJ"
        "E PRIVADO!!", privmsgonly=True)
        core.addCommandHandler("listusers", self, cpriv=1, chelp=
        "Lista los usuarios registrados con el bot.")
        core.addCommandHandler("listpriv", self, chelp=
        "Lista los privilegios de un usuario. Sintaxis: listpriv <usuario>")
        core.addCommandHandler("addpriv", self, cpriv=9, chelp=
        "Añade un privilegio o modifica uno existente. Sintaxis: addpriv"
        " <usuario> <privilegio> [modulo] [canal] (si modulo o canal no se esp"
        "ecifican, serán \"*\"", cprivchan=True)
        core.addCommandHandler("delpriv", self, cpriv=9, chelp=
        "Elimina un privilegio o modifica uno existente. Sintaxis: addpriv"
        " <usuario> <privilegio> [modulo] [canal] (si modulo o canal no se esp"
        "ecifican, se borrara el primer privilegio que coincida",
         cprivchan=True)
        core.addCommandHandler("deluser", self, cpriv=10, chelp=
        "Borra a un usuario del bot. Sintaxis: deluser <usuario>")

    def register(self, bot, cli, ev):
        if len(ev.splitd) != 2:
            cli.privmsg(ev.target, "\00304Error\003: Faltan parametros.")
            return 0
        passw = hashlib.sha1(ev.splitd[1].encode('utf-8')).hexdigest()

        u = User.get(User.name == ev.splitd[0].lower())
        if u is False:
            u = User()
            u.name = ev.splitd[0].lower()
            u.password = passw
            u.save()
            # Si no hago esto no puedo obtener el uid :\
            user = User.get(User.name == ev.splitd[0].lower())
            UserPriv.create(uid=user.uid, priv=0, secmod="*", secchan="*")
            cli.privmsg(ev.target, "Te has registrado exitosamente. Ahora"
            " debes identificarte (\2{0}help auth\2)".format(bot.conf['prefix']
            ))
        else:
            cli.privmsg(ev.target, "\00304Error\003: Ya estás registrado.")

    def listusers(self, bot, cli, ev):
        users = User.select()
        resp = "Usuarios registrados: "
        for user in users:
            resp += user.name + " "
        cli.privmsg(ev.target, resp)

    def listpriv(self, bot, cli, ev):
        if not len(ev.splitd) > 0:
            cli.privmsg(ev.target, "\00304Error\003: Faltan parametros.")
            return 0
        user = User.get(User.name == ev.splitd[0].lower())
        if user is False:
            cli.privmsg(ev.target, "\003Error\003: El usuario no existe.")
        else:
            resp = "El usuario \2{0}\2 tiene los siguientes privilegios:" \
                .format(user.name)
            privs = UserPriv.select().where(UserPriv.uid == user.uid)
            for priv in privs:
                resp += " \2{0}\2 en el módulo \2{1}\2 en el canal \2{2}\2" \
                    .format(priv.priv, priv.secmod, priv.secchan)
            cli.privmsg(ev.target, resp)

    def delpriv_p(self, bot, cli, ev):
        return self.addpriv_p(bot, cli, ev)

    def addpriv_p(self, bot, cli, ev):
        if len(ev.splitd) > 3:
            return ev.splitd[3]
        else:
            return 0

    def addpriv(self, bot, cli, ev):
        if not len(ev.splitd) > 1:
            cli.privmsg(ev.target, "\00304Error\003: Faltan parametros.")
            return 0
        #guh
        uname = ev.splitd[0]
        priv = int(ev.splitd[1])
        if len(ev.splitd) > 2:
            module = ev.splitd[2]
        else:
            module = "*"

        if len(ev.splitd) > 3:
            chan = ev.splitd[3]
        else:
            chan = "*"

        user = User.get(User.name == uname)
        if user is False:
            cli.privmsg(ev.target, "\003Error\003: El usuario no existe")
            return 0

        uprivs = UserPriv.select().where(UserPriv.uid == user.uid)

        p = 0
        for upriv in uprivs:
            if upriv.priv >= priv:
                p += 1
            if upriv.secchan == chan or upriv.secchan == "*":
                p += 1

            if upriv.secmod == module or upriv.secmod == "*":
                p += 1

            if p == 3:
                cli.privmsg(ev.target, "\003Error\003: El usuario ya tiene priv"
                 "ilegios iguales o superiores a los que se intento otorgar.")
                return 0

            if upriv.secchan == chan and upriv.secmod == module:
                upriv.priv = priv
                upriv.save()
                cli.privmsg(ev.target, "Se han otorgado los privilegios.")
                return 0

        UserPriv.create(uid=user.uid, priv=priv, secchan=chan, secmod=module)

        cli.privmsg(ev.target, "Se han otorgado los privilegios.")

    def delpriv(self, bot, cli, ev):
        if not len(ev.splitd) > 1:
            cli.privmsg(ev.target, "\00304Error\003: Faltan parametros.")
            return 0

        #guh x2
        uname = ev.splitd[0]
        priv = int(ev.splitd[1])
        if len(ev.splitd) > 2:
            module = ev.splitd[2]
        else:
            module = "*"

        if len(ev.splitd) > 3:
            chan = ev.splitd[3]
        else:
            chan = "*"

        user = User.get(User.name == uname)
        if user is False:
            cli.privmsg(ev.target, "\003Error\003: El usuario no existe")
            return 0

        uprivs = UserPriv.select().where(UserPriv.uid == user.uid)

        p = 0
        tot = 0
        for upriv in uprivs:
            if upriv.priv >= priv:
                p += 1
            if upriv.secchan == chan or chan == "*":
                p += 1

            if upriv.secmod == module or module == "*":
                p += 1

            if p == 3:
                upriv.delete_instance()
                tot += 1

        if tot == 0:
            cli.privmsg(ev.target, "\003Error\003: No se ha encontrado ningun "
             "privilegio coincidiendo para borrar.")
        else:
            cli.privmsg(ev.target, "Se han borrado {0} privilegios".format(tot))

    def deluser(self, bot, cli, ev):
        if not len(ev.splitd) > 0:
            cli.privmsg(ev.target, "\00304Error\003: Faltan parametros.")
            return 0
        user = User.get(User.name == ev.splitd[0].lower())
        if user is False:
            cli.privmsg(ev.target, "\003Error\003: El usuario no existe.")
        else:
            user.delete_instance()
            cli.privmsg(ev.target, "Se ha eliminado el usuario \2{0}\2".format(
                ev.splitd[0].lower()))