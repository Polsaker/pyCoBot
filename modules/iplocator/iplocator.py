# -*- coding: utf-8 -*-
import http.client
import urllib.request
import urllib.parse
import urllib.error
#import re
import json


class iplocator:

    def __init__(self, core, client):
        core.addCommandHandler("ip", self, chelp=
        "Geolocaliza una ip. Sintaxis: ip <ip>")

    def ip(self, bot, cli, ev):
        if len(ev.splitd) < 1:
            cli.notice(ev.target, "\00304Error\003: Faltan parametros")
            return 0
        text = urllib.parse.quote(ev.splitd[0])
        conn = http.client.HTTPConnection("ip-api.com")
        conn.request("GET", "/json/{0}?fields=65535".format(text))
        res = conn.getresponse().read().decode('utf-8')
        data = json.loads(res)
        if data.status == "success":
            resp = "IP \2{0}\2 ".format(ev.splitd[0])
            if data['reverse'] != "": 
                resp += "- {0} ".format(data['reverse'])
            if data['country'] != "":
                resp += "\2País\2: {0} ".format(data['country'])
            if data['region'] != "":
                resp += "\2Región\2: {0} ".format(data['region'])
            if data['city'] != "":
                resp += "\2Ciudad\2: {0} ".format(data['city'])
            if data['isp'] != "":
                resp += "\2ISP\2: {0} ".format(data['isp'])
            if data['org'] != "":
                resp += "\2Organización\2: {0} ".format(data['org'])
            if data['as'] != "":
                resp += "\2ASN\2: {0} ".format(data['as'])
            if data['timezone'] != "":
                resp += "\2Zona horaria\2: {0} ".format(data['timezone'])
            cli.notice(ev.target, resp)
        else:
            cli.notice(ev.target, "\00304Error\003: No se pudo procesar la IP.")
    
def isset(variable):
	return variable in locals() or variable in globals()
