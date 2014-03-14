import json
import urllib.request
import re


class youtube:
    def __init__(self, core, client):
        try:
            self.apikey = core.mconf['moduleconf']['googleapikey']
            if self.apikey == "":
                return None
        except:
            return None
        core.addHandler("pubmsg", self, "ytlinks")
    
    def ytlinks(self, cli, ev):
        yr = re.compile(".*youtube\.com\/watch\?.*v=([A-Za-z0-9._%-]*)[&\w;=\+_\-]*.*")
        res = yr.search(ev.arguments[0])
        if res is not None:
            r = urllib.request.urlopen("https://www.googleapis.com/youtube/v3/videos?id=" + res.group(1) +"&part=id,contentDetails,statistics,snippet&key=" + self.apikey)
            jao = json.loads(r.read().decode('utf-8'))
            vtitle = jao['items'][0]['snippet']['title']
            views = jao['items'][0]['statistics']['viewCount']
            likes = jao['items'][0]['statistics']['likeCount']
            dislikes = jao['items'][0]['statistics']['dislikeCount']
            comments = jao['items'][0]['statistics']['commentCount']
            duration = jao['items'][0]['contentDetails']['duration']
            tr = re.compile("PT(\d{1,})*H*(\d{1,})M*(\d{1,})S*")
            tm = tr.search(duration)
            m = "00"
            h = "00"
            s = "00"
            try:
                s = tm.group(3)
                m = tm.group(2)
                h = tm.group(1)
                if not h:
                    h = 0
                if not m:
                    m = 0
                if not s:  # ???
                    s = 0
            except:
                pass
            if int(s) < 10:
                s = "0" + str(s)
            if int(m) < 10:
                s = "0" + str(m)
            if int(h) < 10:
                s = "0" + str(h)
            rank = round((int(likes) / (int(likes) + int(dislikes))) * 100)
            resp = "\2%s\2 \00310Duración:\003 %s:%s:%s \00310Visto\003 \2%s\2" \
                " veces, con \00303%s \2Me gusta\2\003, \00305%s \2No me gusta\2\003" \
                " (%s%%) y %s \2comentarios\2" % (vtitle, str(h), str(m), str(s), \
                views, likes, dislikes, rank, comments)
            cli.privmsg(ev.target, resp)

