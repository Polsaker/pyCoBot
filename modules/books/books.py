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

    def book(self, bot, cli, event):
        if len(event.splitd) > 0:
            stext = urllib.parse.quote_plus(" ".join(event.splitd))
        else:
            cli.msg(event.target, "\00304Error\003: Faltan parametros")
            return 0
        
        if re.search("isbn", stext):
            stext = stext.replace("-", "")
        
        r = urllib.request.urlopen("https://www.googleapis.com/books/v1/"
            "volumes?q={0}&orderBy=relevance&key={1}&maxResults=4".format(stext, self.apikey)).read()

        search = json.loads(r.decode('utf-8'))
        if search['totalItems'] == 0:
            cli.msg(event.target, "\00304Error\003: No se ha encontrado ningún libro que coincida con el criterio de búsqueda")
            return

        for b in search['items']:
            resp = "\002{0}\002, Autor(es): \002{1}\002, ".format(
                    b['volumeInfo']['title'], ", ".join(b['volumeInfo']['authors']))
            try:
                resp += "\002{0}\002 páginas. ".format(b['volumeInfo']['pageCount'])
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
