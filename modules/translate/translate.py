import http.client
import urllib.request
import urllib.parse
import urllib.error
import re


class translate:
    def __init__(self, core, client):
        core.addCommandHandler("traducir", self,
        chelp="Traduce un texto. Sintaxis: traducir <de> <a> <texto>;"
        " 'de' puede ser 'auto' para autodetectar el idioma.", alias=
        ['translate', 'tr'])

    def traducir(self, bot, cli, ev):
        if len(ev.splitd) < 2:
            cli.notice(ev.target, "\00304Error\003: Faltan parametros")
            return 0
        self.translate(" ".join(ev.splitd[2:]), ev.splitd[1], ev.splitd[0], cli,
                ev.target)

    def translate(self, text, OUT, IN, cli, to):
        text = urllib.parse.quote(text)
        conn = http.client.HTTPConnection("translate.google.com")
        conn.request("GET", "/translate_a/t?client=t&text=" + text +
                    "&hl=" + IN + "&tl=" + OUT)
        res = conn.getresponse().read()
        p1 = re.compile("\[\[\[\"(.+)\",\"(.*)\",\"(.*)\",\"\"\]\],.*")
        m1 = p1.search(res.decode('utf-8'))
        if m1 is not None:
            translated = m1.group(1)
            ftranslated = m1.group(2)
            pronun = m1.group(3)
            resp = "Traducido: " + ftranslated + " -> " + translated
            if pronun != "":
                resp += " (" + pronun + ")"
        else:
            resp = "No se pudo traducir."

        cli.notice(to, resp)
        #res = res[4:res.index(b",\"\",\"\"]]")]
        #res = res.split(b"],[")
        #for i in range(len(res)):
            #if i >= 1:
                #res[i] = res[i][1:res[i].index(b"\",\"")]
            #else:
                #res[i] = res[i][:res[i].index(b"\",\"")]
        #return str(res[0])[2:len(str(res[0])) - 1]
