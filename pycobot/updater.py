# -*- coding: utf-8 -*-
import urllib.request
import json
import logging
import hashlib
import os


class pyCoUpdater:

    def __init__(self, cli, ev, conf, bot):
        self.bot = bot
        self.cli = cli
        self.conf = conf
        self.ev = ev
        self.githttpupd = {}
        self.upd = False
        self.restartupd = False

    def addfile(self, utype, module, user="", repo="", url=""):
        if utype == "github":
            # TODO: Actualizador vía github api
            try:
                self.githttpupd[user + "/" + repo]
            except KeyError:
                self.githttpupd[user + "/" + repo] = []
            self.githttpupd[user + "/" + repo].append(module)
        elif utype == "github-http":
            try:
                self.githttpupd[user + "/" + repo]
            except KeyError:
                self.githttpupd[user + "/" + repo] = []
            self.githttpupd[user + "/" + repo].append(module)
        elif utype == "http":
            pass  # TODO: Actualizador vía http normal

    def update(self):
        self.preprocessgithttp()
        # self.preprocessgithub()
        # self.preprocesshttp()
        self.modrepos()
        self.coreupdate()

        if self.upd is False:
            self.cli.privmsg(self.ev.target, "No hay actualizaciones " +
             " disponibles")
        print("updend")
        return self.restartupd

    def modrepos(self):
        for x, xval in enumerate(self.conf['modulerepos']):
            if xval['autodownload'] is True:
                ix = urllib.request.urlopen('https://github.com/%s/ra' % (xval[
                 'location']) + 'w/master/index.json').read()
                index = json.loads(ix.decode('utf-8'))
                for x, val in enumerate(index['modules']):
                    try:
                        open("modules/%s/%s.py" % (val, val))
                    except:
                        val = "modules/%s/%s" % (val, val)
                        if self.processgithttp(xval['location'], val + ".py") \
                         is True:
                            self.processgithttp(xval['location'], val + ".json")
                            self.upd = True
                            self.cli.privmsg(self.ev.target, "\2Actualizando " +
                             "\00303" + val + "\00307\2 [Nuevo]")

    def coreupdate(self):
        # TODO: Descargar archivos nuevos
        logging.info("Descargando índice de archivos del nucleo...")
        ix = urllib.request.urlopen('https://github.com/irc-CoBot/pyCoBot/ra' +
         'w/master/pycobot/index.json').read()
        index = json.loads(ix.decode('utf-8'))
        for x, xval in enumerate(index):
            if self.processgithttp("irc-CoBot/pyCoBot", "pycobot/" + xval) is \
             True:
                self.cli.privmsg(self.ev.target, "\2Actualizando \00303" +
                 "pycobot/" + xval)
                self.upd = True
                self.restartupd = True

        # \o/
        if self.processgithttp("irc-CoBot/pyCoBot", "pycobot.py") is True:
            self.cli.privmsg(self.ev.target, "\2Actualizando \00303pycobot.py")
            self.upd = True
            self.restartupd = True
        if self.processgithttp("irc-CoBot/pyCoBot", "irc/client.py") is True:
            self.cli.privmsg(self.ev.target, "\2Actualizando \00303irc/clien" +
            "t.py")
            self.upd = True
            self.restartupd = True

    def preprocessgithttp(self):
        # TODO: Auto-descarga de módulos no encontrados localmente
        for i in enumerate(self.githttpupd):
            i = i[1]
            logging.info("Descargando indice de modulos github-http para el " +
            "repositorio %s" % i)
            ix = urllib.request.urlopen('https://github.com/%s/raw' % i +
             '/master/index.json').read()  # Obtenemos el indice de modulos..
            index = json.loads(ix.decode('utf-8'))
            for k, val in enumerate(self.githttpupd[i]):
                for x, xval in enumerate(index['modules']):
                    if val == xval:

                        if self.processgithttp(i, "modules/" + val + "/" + val +
                         ".py") is True:
                            self.cli.privmsg(self.ev.target,
                             "\2Actualizando \00303%s" % "modules/" + val)
                            self.upd = True
                            try:
                                # si esta cargado...
                                self.bot.modinfo[val]
                                # ... lo recargamos...
                                self.bot.unloadmod(val)
                                self.bot.loadmod(val, self.cli)
                            except:
                                pass  # ???

    def processgithttp(self, repo, path):
        response = urllib.request.urlopen('https://github.com/%s/raw' % (repo) +
        '/master/%s' % path).read()
        try:
            f = open(path)
            fh = hashlib.sha1(f.read().encode('utf-8')).hexdigest()
            f.close()
        except:
            fh = 0

        oh = hashlib.sha1(response).hexdigest()
        if not fh == oh:
            logging.info("Actualizando %s. Hash local: %s. Hash remoto: %s" % (
             path, fh, oh))

            ensure_dir(path)
            f = open(path, "w")
            f.write(str(response))
            f.close()
            return True
        else:
            return False


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)