# -*- coding: utf-8 -*-
import pycurl
from io import BytesIO
import urllib.parse
#import execjs
import re
from html.parser import HTMLParser

class rae:

    abbr_regex = re.compile('<abbr .*?title=\"(.+?)\">.+?<\/abbr>', re.IGNORECASE)
    mark_regex = re.compile('<\/?mark ?.*?>', re.IGNORECASE)
    green_regex = re.compile('<p class=\"n(2|3)\">(.+?)<\/p>', re.IGNORECASE)
    red_regex = re.compile('<p class=\"k.?\".*?>(.+?)<\/p>', re.IGNORECASE)
    
    numberdot = re.compile('(\d\.)')
    
    def __init__(self, core, client):
        core.addCommandHandler("rae", self, alias=['drae', 'def', 'ety'], chelp=
        "Busca una palabra en el diccionario de la Real Academia Española. Uso: rae <palabra>")

    def ircify(self, html):
        html = html.replace("<em>", "\002").replace("</em>", "\002")
        html = self.green_regex.sub("(\\2) ", html)
        html = self.red_regex.sub("\002\00305\\1\003\002 ", html)
        html = self.abbr_regex.sub("\00302\\1\003", html)
        
        html = self.numberdot.sub("\002\\1\002", html)
        return html
    
    def strip_tags(self, html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

    def rae(self, bot, cli, event):
        if len(event.splitd)  == 0:
            cli.msg(event.target, "\00304Error\003: Faltan parametros")
            return 0
        buffer = BytesIO()

        palabra = urllib.parse.quote_plus(event.splitd[0].lower())
        
        c = pycurl.Curl()
        c.setopt(c.URL, 'http://dle.rae.es/srv/search?w='+palabra)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.USERAGENT, "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36")
        c.perform()
        
        body = buffer.getvalue().decode()
        
        t1 = body.split("<article ")[1].split("</article>")[0]
        did = t1.split("\n")[0].replace("id=\"", '').replace("\">", '')

        defs = t1.split("\n")[2:-1]

        p = "\002{0}\002:".format(event.splitd[0].lower())

        for defi in defs:            
            df = self.mark_regex.sub("", defi)
            p += " " + df
        
        cli.msg(event.target, self.strip_tags(self.ircify(p))[:800] + "…")
        cli.msg(event.target, "\00310" + 'http://dle.rae.es/?w='+palabra)
        
        
    def oldrae(self, bot, cli, event):
        if len(event.splitd)  == 0:
            cli.msg(event.target, "\00304Error\003: Faltan parametros")
            return 0
        palabra = urllib.parse.quote_plus(event.splitd[0])
        buffer = BytesIO()

        c = pycurl.Curl()
        c.setopt(c.URL, 'http://lema.rae.es/drae/srv/search?key='+palabra)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()

        body = buffer.getvalue()
        l = body.decode().split("<script>")[1].split("</script>")[1].replace('<script type="text/javascript">', '').replace('document.forms[0].elements[1].value=', 'return ')
        ctx = execjs.compile(l)
        chall = ctx.call("challenge")
        pdata = "&".join(body.decode().split("<body")[1].replace("/>", "\n").split("\n")[1:-1]).replace('<input type="hidden" name="', '').replace('" value="', '=').replace('"','').replace('TS014dfc77_cr=', 'TS014dfc77_cr=' + urllib.parse.quote_plus(chall))

        buffer = BytesIO()

        c = pycurl.Curl()
        c.setopt(c.URL, 'http://lema.rae.es/drae/srv/search?key='+palabra)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(pycurl.HTTPHEADER, ["Referer: http://lema.rae.es/drae/srv/search?key=hola",
        "Cache-Control: max-age=0",
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Origin: http://lema.rae.es",
        "User-Agent: Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/39.0.2171.65 Chrome/39.0.2171.65 Safari/537.36"
        ])
        c.setopt(pycurl.VERBOSE, 1)
        c.setopt(c.POSTFIELDS, pdata)
        c.perform()
        body = buffer.getvalue().decode()
        
        ht = self.strip_tags(self.ircify(body))
#        print(ht.split("(function")[0].split("\n\n\n\n"))
#        p = self.strip_tags(ht).split("Real Academia")[1].split("\n\n\n\n")[1]
        p = ht.split("(function")[0].split("\n\n\n\n")[2].replace("Real Academia Española © Todos los derechos reservados\n", '').replace('\n', '')       
        cli.msg(event.target, p[:800] + "…")
        cli.msg(event.target, "\00310" + 'http://lema.rae.es/drae/srv/search?key='+palabra)


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
    def handle_entityref(self, name):
        self.fed.append('&%s;' % name)

