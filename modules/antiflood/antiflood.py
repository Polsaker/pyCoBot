# -*- coding: utf-8 -*-
from pycobot.tables import User, UserPriv



class antiflood:
    def __init__(self, core, client):
        core.addCommandHandler("antiflood", self, cpriv=5, chelp=
        "Maneja el antiflood de un canal. Sintaxis: antiflood <canal> <on/off>"
        " [mensajes] [segundos]", cprivchan=True)
        core.addHandler("pubmsg", self, "pubmsghandle")
    
    def pubmsghandle(self, cli, ev):
        pass  # TODO

    def antiflood_p(self, bot, cli, ev):
        if len(ev.splitd) > 2:
            return ev.splitd[1]
        else:
            return 0

    def antiflood(self, bot, cli, ev):
        if not len(ev.splitd) > 1:
            cli.privmsg(ev.target, "\00304Error\003: Faltan parametros.")
            return 0
        ul = AntiFloodChan.get(AntiFloodChan.chan == ev.splitd[0])
        if ev.splitd[1] == "on":
            if not len(ev.splitd) > 3:
                cli.privmsg(ev.target, "\00304Error\003: Faltan parametros.")
                return 0
            if not ul is False:
                ul.ratesec = ev.splitd[3]
                ul.ratemsg = ev.splitd[2]
                ul.save()
            else:
                AntiFloodChan.create(chan=ev.splitd[0], ratesec=ev.splitd[3], ratemsg=ev.splitd[2])
            cli.privmsg(ev.target, "Se ha activado el antiflood en \2{0}\2".format(ev.splitd[0]))
        elif ev.splitd[1] == "off":
            if ul is False:
                cli.privmsg(ev.target, "\00304Error\003: El antiflood no esta activado en ese canal.")
            else:
                ul.delete_instance()
                cli.privmsg(ev.target, "Se ha desactivado el antiflood en \2{0}\2".format(ev.splitd[0]))
        

class AntiFloodChan(BaseModel):
    cid = IntegerField(primary_key=True)
    chan = CharField()
    ratesec = IntegerField()
    ratemsg = IntegerField()
