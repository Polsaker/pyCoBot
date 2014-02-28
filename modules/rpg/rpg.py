# -*- coding: utf-8 -*-
from pycobot.pycobot import BaseModel
from peewee.peewee import CharField, IntegerField


class rpg:
    def __init__(self, core, client):
        # Copy & Paste de m_games >:D
        self.timehandlers = ""
        l = False
        for k in core.botcli.bots:
            import pprint
            if k.is_loaded("rpg") is True:
                #pprint.pprint(k.getmodule("rpg").timehandlers)
                #pprint.pprint(k.getmodule("rpg"))
                if k.getmodule("rpg").timehandlers == k.getmodule("rpg"):
                    self.timehandlers = k.getmodule("rpg")
                l = True
        
        if l is False:
            self.timehandlers = self
            #core.addTimeHandler(1800, self, "th30min")
            #core.addTimeHandler(1800, self, "th15min")
        
        try:
            RPGChannel.create_table()
            RPGUser.create_table()
        except:
            pass
        
        core.addHandler("pubmsg", self, "commandhandle2")
        core.addHandler("privmsg", self, "commandhandle")
    
    def commandhandle2(self, cli, ev):
        c = RPGChannel.get(RPGChannel.channel == ev.target)
        if c is False:
            return 1  # "Los juegos no están habilitados en este canal.."
        else:
            self.commandhandle(cli, ev)

    def commandhandle(self, cli, ev):
        if not ev.splitd[0][0] == "!":
            return 0
        com = ev.splitd[0][1:]
        del ev.splitd[0]
        
        if com == "alta" or com == "start":
            self.alta(cli, ev)
            return 1
        
        # Comandos normales
        if com == "stats":
            func = "stats" # meh...
        else:
            return 3  # "Comando/funcion inexistente"
        
        user = RPGUser.get(RPGUser.nick == ev.source)
        if user is False:
            self.msg(ev, "No estás dado de alta en el juego. Para"
                " darte de alta escribe \2!alta\2", True)
                return 2  # "No estás dado de alta en el juego"
        else:
            getattr(self, func)(user, cli, ev)
                
        
    
class RPGChannel(BaseModel):
    cid = IntegerField(primary_key=True)
    channel = CharField()

class RPGUser(BaseModel):
    uid = IntegerField(primary_key=True)
    nick = CharField()
    empirename = CharField()
    superficie = IntegerField()
    congelado = IntegerField()  # ;D
    habitantes = IntegerField()
    tropas = IntegerField()
    tropas_nivel = IntegerField()
    deuda = IntegerField()
    oro = IntegerField()
    alimento = IntegerField()
    madera = IntegerField()
    piedra = IntegerField()
    flota = IntegerField()
    extrainf = CharField()
