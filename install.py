#!/usr/bin/python
# -*- coding: utf-8 -*-

print("Bienvenido/a al instalador de CoBot 2.0 (Gizkard)")
config = {}
config['modulerepos'] = [{'location': 'irc-CoBot/pyCoBot', 
                                    "autodownload": True}]
config['conf'] = {'loglevel': 'info', 'logfile': ''}
config['irc'] = {}


def addNetwork():
    netname = inp("Introduzca el nombre de la red/servidor (solo el nombre, un"
            "icamenzte alfanumerico)")
    if netname == "":
        addNetwork()
        return
    server = inp("Introduzca la dirección del servidor IRC (Por ejemplo, irc.freenode.net)")
    if server == "":
        addNetwork()
        return
    port = inp("Puerto", 6667)
    #ssl = inp("SSL?", "No")
    nick = inp("Nick del bot", "pyCoBot")
    prefix = inp("Prefijo de los comandos", "-")
    
    # TODO: Iterar sobre todos los modulos, ofrecer su descripcion y preguntar al usuario si activarlos o no.


def inp(text, default=""):
    if default != "":
        text += " [{0}]".format(str(default))
    text += ": "
    ret = input(text)
    if ret == "":
        return default
    else:
        return ret
        
addNetwork()
