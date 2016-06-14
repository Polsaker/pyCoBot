# -*- coding: utf-8 -*-
import pycurl
from io import BytesIO
import urllib.parse
#import execjs
import re
from html.parser import HTMLParser

BASE_URL = "http://dle.rae.es/srv/"

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

        palabra = urllib.parse.quote_plus(event.splitd[0].lower())
        url = BASE_URL + 'search?w='+palabra
        body = retrieve_website(url)

        p = None
        if "<article" in body:
            # If an article, parse it
            p = self.parse_article(palabra, body)

        elif "<ul" in body:
            # If a link page, follow the first link
            parser = LinkParser()
            parser.feed(body)

            if len(parser.links) > 0:
                body = retrieve_website(BASE_URL + parser.links[0])
                p = self.parse_article(palabra, body)

        if p:
            cli.msg(event.target, self.strip_tags(self.ircify(p))[:400] + "…")
            cli.msg(event.target, "\00310" + 'http://dle.rae.es/?w='+palabra)
        else:
            cli.msg(event.target, "La palabra {} no está en el Diccionario".format(palabra))

    def parse_article(self, palabra, body):
        t1 = body.split("<article ")[1].split("</article>")[0]
        # did = t1.split("\n")[0].replace("id=\"", '').replace("\">", '')

        defs = t1.split("\n")[2:-1]

        p = "\002{0}\002:".format(palabra)

        for defi in defs:            
            df = self.mark_regex.sub("", defi)
            p += " " + df

        return p


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


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for (key, val) in attrs:
                if key == 'href':
                    self.links.append(val)

    handle_startendtag = handle_starttag


def retrieve_website(website):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, website)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.USERAGENT, "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36")
    c.perform()
    return buffer.getvalue().decode()

