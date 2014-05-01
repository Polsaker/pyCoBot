import urllib2


class translate:
    def __init__(self, core, client):
        core.addCommandHandler("traducir", self,
        chelp="Traduce un texto. Sintaxis: traducir <de> <a> <texto>;"
        " 'de' puede ser 'auto' para autodetectar el idioma.", alias=
        ['translate', 'tr'])


    def traducir(self, client, ev):
        if len(ev.splitd) < 2:
            cli.notice(ev.target, "\00304Error\003: Faltan parametros")
            return 0
        cli.notice(ev.target, "Traducido: {0}".format(
            translate(" ".join(ev.splitd[2:]), ev.splitd[1], ev.splitd[0])))
    
    def translate(to_translate, to_langage="auto", langage="auto"):
        agents = {'User-Agent':"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)"}
        before_trans = 'class="t0">'
        link = "http://translate.google.com/m?hl=%s&sl=%s&q=%s" % (to_langage, langage, to_translate.replace(" ", "+"))
        request = urllib2.Request(link, headers=agents)
        page = urllib2.urlopen(request).read()
        result = page[page.find(before_trans)+len(before_trans):]
        result = result.split("<")[0]
        return result
