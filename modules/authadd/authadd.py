# -*- coding: utf-8 -*-
from pycobot.tables import User, UserPriv
import hashlib


class authadd:
    def __init__(self, core, client):
        core.addCommandHandler("register", self, chelp="Registra un usuario con"
        " el bot. Sintaxis: register <usuario> <contraseña> USAR SOLO EN MENSAJ"
        "E PRIVADO!!", privmsgonly=True)

    def register(self, bot, cli, ev):
        if len(ev.splitd) != 2:
            cli.privmsg(ev.target, "\00304Error\003: Faltan parametros.")
            return 0
        passw = hashlib.sha1(ev.splitd[1].encode('utf-8')).hexdigest()

        u = User.get(User.name == ev.splitd[0].lower())
        if u is False:
            user = User.create(name=ev.splitd[0].lower(), password=passw)
            UserPriv.create(uid=user.uid, priv=0, secmod="*", secchan="*")
            cli.privmsg(ev.target, "Te has registrado exitosamente. Ahora"
            " debes identificarte (\2{0}help auth\2)".format(bot.conf['prefix']
            ))
        else:
            cli.privmsg(ev.target, "\00304Error\003: Ya estás registrado.")