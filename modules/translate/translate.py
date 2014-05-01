import http.client, urllib.request, urllib.parse, urllib.error, string


class translate:
    def __init__(self, core, client):
        core.addCommandHandler("traducir", self,
        chelp="Traduce un texto. Sintaxis: traducir <de> <a> <texto>;"
        " 'de' puede ser 'auto' para autodetectar el idioma.", alias=
        ['translate', 'tr'])


    def traducir(self, bot, client, ev):
        if len(ev.splitd) < 2:
            bot.notice(ev.target, "\00304Error\003: Faltan parametros")
            return 0
        bot.notice(ev.target, "Traducido: {0}".format(
            self.translate(" ".join(ev.splitd[2:]), ev.splitd[1], ev.splitd[0])))
    
    def translate(self, text, OUT, IN):
        text = urllib.parse.quote(text)
        conn = http.client.HTTPConnection("translate.google.com")
        conn.request("GET", "/translate_a/t?client=t&text="+text+"&hl="+IN+"&tl="+OUT)
        res = conn.getresponse().read()
        res = res[4:res.index(b",\"\",\"\"]]")]
        res = res.split(b"],[")
        for i in range(len(res)):
            if i >= 1: res[i] = res[i][1:res[i].index(b"\",\"")]
            else:      res[i] = res[i][:res[i].index(b"\",\"")]
        return res[0]
