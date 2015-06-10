# -*- coding: utf-8 -*-
import string
import random
import json
import urllib.request
import urllib.parse

class cumbia:
    def __init__(self, core, client):
        try:
            self.apikey = core.readConf("config.googleapikey")
            if self.apikey == "":
                return
        except:
            return
        core.addCommandHandler("cumbia", self)  

    def cumbia(self, bot, cli, ev):
        topic = "/m/02ccj9"
        if len(ev.splitd) > 0:
            if ev.splitd[0] == "villera":
                topic = "/m/06wdnn"
            elif ev.splitd[0] == "argentina":
                topic = "/m/06wdnn"
            elif ev.splitd[0] == "peruana":
                topic = "/m/0h9xfdy"
            elif ev.splitd[0] == "mexicana":
                topic = "/m/07ns61"
            elif ev.splitd[0] == "sonidera":
                topic = "/m/03w9y05"
            elif ev.splitd[0] == "rap":
                topic = "/m/04xbt7"
        
        topic = urllib.parse.quote_plus(topic)
        r = urllib.request.urlopen("https://www.googleapis.com/youtube/v3/search?part=snippet&topicId={1}&q={2}&relevanceLanguage=es&maxResults=50&key={0}"
                                    .format(self.apikey, topic, random.choice(string.ascii_lowercase))).read()

        search = json.loads(r.decode('utf-8'))
        
        video = "https://youtube.com/watch?v=" + random.choice(search['items'])['id']['videoId']
        ev.arguments[0] = video
        cli.msg(ev.target, ev.arguments[0])
        bot.modules['links'].linksh(cli, ev)

