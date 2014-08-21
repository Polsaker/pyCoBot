# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.parse
import re


class books:

    def __init__(self, core, client):
        try:
            self.apikey = core.readConf("config.googleapikey")
            if self.apikey == "":
                return
        except:
            return
        core.addCommandHandler("book", self, chelp=
        "Busca libros en Google Libros. Sintaxis: book <término de busqueda> (tip: Usar \"isbn:IDENTIFICADOR_ISBN\" para buscar por ISBN)",
        alias=["libro", "books"])
        self.langs = {}
        self.langs['en'] = "inglés"
        self.langs['es'] = "español"
        self.langs['af'] = "afrikáans"
        self.langs['sq'] = "albanés"
        self.langs['de'] = "alemán"
        self.langs['ar'] = "árabe"
        self.langs['hy'] = "armenio"
        self.langs['az'] = "azerí"
        self.langs['bn'] = "bengalí"
        self.langs['be'] = "bielorruso"
        self.langs['bs'] = "bosnio"
        self.langs['bg'] = "búlgaro"
        self.langs['kn'] = "canarés"
        self.langs['ca'] = "catalán"
        self.langs['ceb'] = "cebuano"
        self.langs['cs'] = "checo"
        self.langs['zh-CN'] = "chino simplificado"
        self.langs['zh-TW'] = "chino tradicional"
        self.langs['ko'] = "coreano"
        self.langs['ht'] = "criollo haitiano"
        self.langs['hr'] = "croata"
        self.langs['da'] = "danés"
        self.langs['sk'] = "eslovaco"
        self.langs['sl'] = "esloveno"
        self.langs['et'] = "estonio"
        self.langs['eu'] = "euskera"
        self.langs['fi'] = "finlandés"
        self.langs['fr'] = "francés"
        self.langs['cy'] = "galés"
        self.langs['gl'] = "gallego"
        self.langs['ka'] = "georgiano"
        self.langs['el'] = "griego"
        self.langs['gu'] = "gujarati"
        self.langs['ha'] = "hausa"
        self.langs['iw'] = "hebreo"
        self.langs['hi'] = "hindi"
        self.langs['hmn'] = "hmong"
        self.langs['nl'] = "holandés"
        self.langs['hu'] = "húngaro"
        self.langs['ig'] = "igbo"
        self.langs['id'] = "indonesio"
        self.langs['en'] = "inglés"
        self.langs['ga'] = "irlandés"
        self.langs['is'] = "islandés"
        self.langs['it'] = "italiano"
        self.langs['ja'] = "japonés"
        self.langs['jw'] = "javanés"
        self.langs['km'] = "jemer"
        self.langs['lo'] = "lao"
        self.langs['la'] = "latín"
        self.langs['lv'] = "letón"
        self.langs['lt'] = "lituano"
        self.langs['mk'] = "macedonio"
        self.langs['ms'] = "malayo"
        self.langs['mt'] = "maltés"
        self.langs['mi'] = "maorí"
        self.langs['mr'] = "maratí"
        self.langs['mn'] = "mongol"
        self.langs['ne'] = "nepalí"
        self.langs['no'] = "noruego"
        self.langs['fa'] = "persa"
        self.langs['pl'] = "polaco"
        self.langs['pt'] = "portugués"
        self.langs['pa'] = "punjabí"
        self.langs['ro'] = "rumano"
        self.langs['ru'] = "ruso"
        self.langs['sr'] = "serbio"
        self.langs['so'] = "somalí"
        self.langs['sw'] = "suajili"
        self.langs['sv'] = "sueco"
        self.langs['tl'] = "tagalo"
        self.langs['th'] = "tailandés"
        self.langs['ta'] = "tamil"
        self.langs['te'] = "telugu"
        self.langs['tr'] = "turco"
        self.langs['uk'] = "ucraniano"
        self.langs['ur'] = "urdu"
        self.langs['vi'] = "vietnamita"
        self.langs['yi'] = "yidis"
        self.langs['yo'] = "yoruba"
        self.langs['zu'] = "zulú"

    def book(self, bot, cli, event):
        if len(event.splitd) > 0:
            stext = urllib.parse.quote_plus(" ".join(event.splitd))
        else:
            cli.msg(event.target, "\00304Error\003: Faltan parametros")
            return 0
        
        foo = re.search("( |^)lang:(.+)( |$)", stext)
        lang = ""
        if foo:
            stext = stext.replace(foo.group(0), "")
            lang = foo.group(2)
        
        if re.search("isbn", stext):
            stext = stext.replace("-", "")
        
        r = urllib.request.urlopen("https://www.googleapis.com/books/v1/"
            "volumes?q={0}&langRestrict={2}&key={1}&maxResults=4".format(stext, self.apikey, lang)).read()

        search = json.loads(r.decode('utf-8'))
        if search['totalItems'] == 0:
            cli.msg(event.target, "\00304Error\003: No se ha encontrado ningún libro que coincida con el criterio de búsqueda")
            return

        for b in search['items']:
            resp = "\002{0}\002, Autor(es): \002{1}\002. ".format(
                    b['volumeInfo']['title'], ", ".join(b['volumeInfo']['authors']))
            try:
                resp += "\002{0}\002 páginas. ".format(b['volumeInfo']['pageCount'])
            except:
                pass
            
            try:
                try:
                    idi = self.langs[b['volumeInfo']['language']]
                except:
                    idi = b['volumeInfo']['language']
                resp += "Idioma: \002{0}\002. ".format(idi)
            except:
                pass
                
            #resp += " ISBN-10: \002{0}\002, ISBN-13: \002{0}\002. ".format( 
            for l in b['volumeInfo']['industryIdentifiers']:
                if l['type'] == "ISBN_13":
                    resp += "ISBN-13: \002{0}\002. ".format(l['identifier'])
                elif l['type'] == "ISBN_10":
                    resp += "ISBN-10: \002{0}\002. ".format(l['identifier'])
            resp += "\00311http://books.google.com/books?id={0}\003".format(b['id'])
            
            cli.msg(event.target, resp)
