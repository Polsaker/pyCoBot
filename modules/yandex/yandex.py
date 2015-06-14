# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.parse


class yandex:

    def __init__(self, core, client):
        try:
            self.apikey = core.readConf("config.yandexkey")
            if self.apikey == "":
                return
        except:
            return
        core.addCommandHandler("traducir", self, alias=['tr', 't', 'tra'], chelp=
        "Traduce utilizando Yandex.Translate. Uso: traducir <de-a> <texto>")

    def traducir(self, bot, cli, event):
        if len(event.splitd) > 1:
            stext = urllib.parse.quote_plus(" ".join(event.splitd[1:]))
        else:
            cli.msg(event.target, "\00304Error\003: Faltan parametros")
            return 0
        r = urllib.request.urlopen("https://translate.yandex.net/api/v1.5/tr.json/translate?lang={2}&text={1}&key={0}&ui=en"
         .format(self.apikey, stext, event.splitd[0])).read()

        search = json.loads(r.decode('utf-8'))

        try:
            resp = "\00304Error\003: " + search['message']
        except:
            resp = "Traduciendo de \002{0}\002 a \002{1}\002: {2}".format(event.splitd[0].split("-")[0], event.splitd[0].split("-")[1], search['text'][0])

        cli.msg(event.target, resp)
