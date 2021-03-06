# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.parse


class google:

    def __init__(self, core, client):
        try:
            self.apikey = core.readConf("config.googleapikey")
            if self.apikey == "":
                return
        except:
            return
        core.addCommandHandler("google", self, chelp=
        "Realiza una busqueda en google. Sintaxis: google <texto>")

    def google(self, bot, cli, event):
        if len(event.splitd) > 0:
            stext = urllib.parse.quote_plus(" ".join(event.splitd))
        else:
            cli.msg(event.target, "\00304Error\003: Faltan parametros")
            return 0
        r = urllib.request.urlopen("https://www.googleapis.com/customsearch/v1?"
         "num=3&key=%s&cx=001206920739550302428:fozo2qblwzc&q=%s&alt=json" %
         (self.apikey, stext)).read()

        search = json.loads(r.decode('utf-8'))

        resp = "Resultados de la búsqueda en Google de " + \
        " \"\2{0}\2\": ".format(" ".join(event.splitd)) \
        + "\2%s\2 \037\00310%s\003\037" % (search['items'][0]['title'],
        search['items'][0]['link'])
        try:
            resp += ", \2{0}\2 \037\00310{1}\003\037".format(
                    search['items'][1]['title'], search['items'][1]['link'])
            resp += ", \2{0}\2 \037\00310{1}\003\037".format(
                    search['items'][2]['title'], search['items'][2]['link'])
        except:
            pass

        cli.msg(event.target, resp)
