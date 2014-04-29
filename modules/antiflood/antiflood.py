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
        
        if ev.splitd[1] == "on":
            pass
        elif ev.splitd[1] == "off":
            pass
        

class AntiFloodChan(BaseModel):
    cid = IntegerField(primary_key=True)
    chan = CharField()
    ratesec = IntegerField()
    ratemsg = IntegerField()
