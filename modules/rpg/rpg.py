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
        pass  # TODO: Checkear si se puede jugar en el canal y llamar a commandhandle
    
    def commandhandle(self, cli, ev):
        pass  # TODO: verificar autenticacion, comandos, etc
    
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
