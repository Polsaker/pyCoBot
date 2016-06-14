# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.parse


class partido:

    def __init__(self, core, client):
        core.addCommandHandler("partido", self, chelp=
        "Muestra la afiliación política de una persona. Uso: partido <nombre completo> (Salve pyderechibot.)")

    def partido(self, bot, cli, event):
        if len(event.splitd) > 0:
            if event.splitd[0] == "dlcast" or event.splitd[0] == "dlcastc" or event.splitd[0] == "dlc":
                cli.msg(event.target, "\002{0}\002 milita en el \002partido de la plaza roja".format(event.splitd[0]))
                return
            stext = urllib.parse.quote_plus(" ".join(event.splitd))
        else:
            cli.msg(event.target, "\00304Error\003: Faltan parametros")
            return 0

        wd = urllib.request.urlopen("https://www.wikidata.org/w/api.php?action=wbgetentities&sites=eswiki&titles={0}&languages=es&normalize=&props=claims&format=json".format(stext)).read().decode('utf-8', 'replace')
        
        wd = json.loads(wd)
        
        e = wd['entities'][list(wd['entities'].keys())[0]]
        
        partido = None
        
        for i in e['claims']:
            if i == "P102":
                prop = e['claims']['P102'][0]['mainsnak']['datavalue']['value']['numeric-id']
                wprop = urllib.request.urlopen("https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q{0}&languages=es&props=labels&format=json".format(prop)).read().decode('utf-8', 'replace')
                partido = json.loads(wprop)["entities"]["Q" + str(prop)]['labels']['es']['value']

        try:
            nombre = wd['normalized']['n']['to']
        except:
            nombre = " ".join(event.splitd)
        
        if not partido:
            cli.privmsg(event.target, "\00304Error\003: No se pudo obtener la información de la afiliación política de esa persona!")
        elif partido.startswith("Partido") == True:
            cli.msg(event.target, "\002{0}\002 milita en el \002(1)".format(nombre,partido))
        else:
            cli.msg("\002{0}\002 milita en \002{1}".format(nombre,partido))
