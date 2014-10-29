import json
import urllib.request
import re
from html.parser import HTMLParser
from pycobot.pycobot import BaseModel
from peewee.peewee import CharField, IntegerField


class links:
    def __init__(self, core, client):
        self.yt = True
        try:
            self.apikey = core.readConf("config.googleapikey")
            if self.apikey == "":
                self.yt = False
        except:
            self.yt = False
        try:
            linkChan.create_table(True)
        except:
            pass
        core.addHandler("pubmsg", self, "linksh")
        core.addCommandHandler("links", self, cpriv=4, chelp=
        "Hace que el bot muestre los títulos de los links. Sintaxis: links #can"
        "al <on/off>", cprivchan=True)
        self.chancache = {}
        self.updatechancache()

    def links_p(self, bot, cli, ev):
        if len(ev.splitd) > 1:
            return ev.splitd[0]
        else:
            return 0

    def links(self, bot, cli, ev):
        if not len(ev.splitd) > 1:
            cli.msg(ev.target, "\00304Error\003: Faltan parametros.")
            return 0
        ul = linkChan.get(linkChan.chan == ev.splitd[0])
        if ev.splitd[1] == "on":
            if not ul is False:
                cli.msg(ev.target, "Esto ya está activado en \2{0}\2".format(
                    ev.splitd[0]))
            else:
                linkChan.create(chan=ev.splitd[0].lower())
                cli.msg(ev.target, "Se han activado los titulos de links "
                                                "en \2{0}".format(ev.splitd[0]))
        elif ev.splitd[1] == "off":
            if ul is False:
                cli.msg(ev.target, "\00304Error\003: Los links no están"
                                                    " activado en ese canal.")
            else:
                ul.delete_instance()
                cli.msg(ev.target, "Se han desactivado los links en "
                                                "\2{0}\2".format(ev.splitd[0]))
        self.updatechancache()

    def updatechancache(self):
        self.chancache = {}
        u = linkChan.select()

        for x in u:
            self.chancache[x.chan] = True

    def linksh(self, cli, ev):
        try:
            self.chancache[ev.target.lower()]
        except:
            return 1
        if self.yt is True:
            yr = re.compile(".*(youtube\.com\/watch\?.*v=|youtu\.be\/)([A-Za-z"
                                                    "0-9._%-]*)[&\w;=\+_\-]*.*")
            res = yr.search(ev.arguments[0])
            if res is not None:
                self.ytlinks(cli, ev, res)
                return 0
        url = re.compile("((https?):((\/\/)|(\\\\))+[\w\d:#@%\/;$()~_?\+-=\\\."
                                                                        "&]*)")
        res = url.search(ev.arguments[0])
        if res is None:
            return 1
        uri = res.group(1)
        r = urllib.request.urlopen(uri).read().decode('utf-8', 'replace')
        parser = HTMLParser()
        r = parser.unescape(r)
        yr = re.compile(".*<title[^>]*>([^<]+)</title>.*")
        title = yr.search(r)
        if title is None:
            return 1

        cli.msg(ev.target, title.group(1).strip())

    def ytlinks(self, cli, ev, res):

        r = urllib.request.urlopen("https://www.googleapis.com/youtube/v"
           "3/videos?id=" + res.group(2) + "&part=id,contentDetails,statist"
           "ics,snippet&key=" + self.apikey)
        jao = json.loads(r.read().decode('utf-8'))
        vtitle = jao['items'][0]['snippet']['title']
        views = jao['items'][0]['statistics']['viewCount']
        likes = jao['items'][0]['statistics']['likeCount']
        dislikes = jao['items'][0]['statistics']['dislikeCount']
        comments = jao['items'][0]['statistics']['commentCount']
        duration = jao['items'][0]['contentDetails']['duration']
        tr = re.compile("PT(?P<hours>\d?\dH)?(?P<minutes>\d?\dM)?(?P<seconds>\d?\dS)?.*")
        tm = tr.search(duration)
        m = "00"
        h = "00"
        s = "00"
        try:
            s = tm.group("seconds")[:-1]
        except:
            s = "00"
        try:
            h = tm.group("hours")[:-1]
        except:
            h = "00"

        try:
            m = tm.group("minutes")[:-1]
        except:
            m = "00"

        if len(s) < 2:
            s = "0" + str(s)
        if len(m) < 2:
            m = "0" + str(m)
        if len(h) < 2:
            h = "0" + str(h)
        rank = round((int(likes) / (int(likes) + int(dislikes))) * 100)
        resp = "\2%s\2 \00310Duración:\003 %s:%s:%s \00310Visto\003 \2%s" \
            "\2 veces, con \00303%s \2Me gusta\2\003, \00305%s \2No me " \
            "gusta\2\003 (%s%%) y %s \2comentarios\2" % (vtitle, h, m, s,
            views, likes, dislikes, rank, comments)
        cli.msg(ev.target, resp)


class linkChan(BaseModel):
    rid = IntegerField(primary_key=True)
    chan = CharField()
