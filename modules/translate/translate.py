import http.client
import urllib.request
import urllib.parse
import urllib.error
#import re
import json


class translate:
    def __init__(self, core, client):
        self.langs = {}
        core.addCommandHandler("traducir", self,
        chelp="Traduce un texto. Sintaxis: traducir <de> <a> <texto>;"
        " 'de' puede ser 'auto' para autodetectar el idioma.", alias=
        ['translate', 'tr'])
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

        #self.langnames = {v: k for k, v in langs.items()}

    def traducir(self, bot, cli, ev):
        if len(ev.splitd) < 2:
            cli.msg(ev.target, "\00304Error\003: Faltan parametros")
            return 0
        self.translate(" ".join(ev.splitd[2:]), ev.splitd[1], ev.splitd[0], cli,
                ev.target, ev.source)

    def translate(self, text, OUT, IN, cli, to, source):
        try:
            if IN != "auto":
                self.langs[IN]
            self.langs[OUT]
        except KeyError:
            resp = "\00304Error\003: Ha ingresado un idioma inválido. "
            presp = resp + "Los idiomas disponibles son: "
            for c, n in self.langs.items():
                presp += n + " (" + c + "), "
            cli.notice(source, presp[0:len(presp) - 2])
            cli.msg(to, resp)
            return 0
        text = urllib.parse.quote(text)
        conn = http.client.HTTPConnection("translate.google.com")
        conn.request("GET", "/translate_a/t?client=p&text=" + text +
                    "&sl=" + IN + "&tl=" + OUT + "&oe=utf-8&ie=utf-8")
        res = conn.getresponse().read()

        trs = json.loads(res.decode('utf-8'))
        try:
            translatd = ""
            translit = ""
            for q in trs['sentences']:
                translatd += q['trans']
                translit += q['translit']
                if q['translit'] != "":
                    translit += " "
                try:
                    src = self.langs[trs['src']]
                except KeyError:
                    src = trs['src']


            resp = "Traducido del \2{0}\2 al \2{1}\2: {2}".format(src,
                                                        self.langs[OUT], translatd)
            if translit != "":
                    resp += " ({0})".format(translit)
        except KeyError:
            resp = "Ocurrió un error al traducir."

        #p1 = re.compile(
            #"\[\[\[\"(.+)\",\"(.*)\",\"(.*)\",\"\"\]\],.*,\"(.{2,5})\",.*,.*")
        #try:
            #m1 = p1.search(res.decode('utf-8'))
        #except:
            #try:
                #m1 = p1.search(res.decode('latin-1'))
            #except:
                #m1 = p1.search(res.decode('utf-8', 'replace'))
        #if m1 is not None:
            #translated = m1.group(1)
            ##ftranslated = m1.group(2)
            #pronun = m1.group(3)
            #try:
                #fromlang = self.langs[m1.group(4)]
            #except:
                #fromlang = m1.group(4)
            #resp = "Traducido del \2{0}\2 al \2{1}\2: {2}".format(fromlang,
                                    #self.langs[OUT], translated)
            #if pronun != "":
                #resp += " (" + pronun + ")"
        #else:
            #resp = "No se pudo traducir."

        cli.msg(to, resp)
        #res = res[4:res.index(b",\"\",\"\"]]")]
        #res = res.split(b"],[")
        #for i in range(len(res)):
            #if i >= 1:
                #res[i] = res[i][1:res[i].index(b"\",\"")]
            #else:
                #res[i] = res[i][:res[i].index(b"\",\"")]
        #return str(res[0])[2:len(str(res[0])) - 1]
