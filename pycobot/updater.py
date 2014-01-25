# -*- coding: utf-8 -*-
import urllib.request
import json
import logging
import pprint
import hashlib
from os import listdir
from os.path import isfile, join


class pyCoUpdater:

    def __init__(self, cli, ev):
        self.cli = cli
        self.ev = ev
        self.githttpupd = {}
        self.upd = False
        self.restartupd = False

    def addfile(self, utype, module, user="", repo="", url=""):
        print(utype)
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
        self.coreupdate()
        if self.upd is False:
            self.cli.privmsg(self.ev.target, "No hay actualizaciones " +
             " disponibles")
        return self.restartupd

    def coreupdate(self):
        for f in listdir("pycobot"):
            if isfile(join("pycobot", f)):
                p = join("pycobot", f)
                if self.processgigithttp("irc-CoBot/pyCoBot", p) is True:
                    self.upd = True
                    self.restartupd = True

    def preprocessgithttp(self):
        pprint.pprint(self.githttpupd)
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
                        if self.processgithttp(i, "modules/" + val + ".py") is \
                         True:
                            self.cli.privmsg(self.ev.target,
                             "\2Actualizando \00303%s" % "modules/" + val)
                            self.upd = True

    def processgithttp(self, repo, path):
        response = urllib.request.urlopen('https://github.com/%s/raw' % (repo) +
        '/master/%s' % path).read()
        f = open(path)
        fh = hashlib.sha1(f.read().encode('utf-8')).hexdigest()
        f.close()
        oh = hashlib.sha1(response).hexdigest()
        if not fh == oh:
            logging.info("Actualizando %s. Hash local: %s. Hash remoto: %s" % (
             path, fh, oh))
            f = open(path, "w")
            f.write(response.decode('utf-8'))
            f.close()
            return True
        else:
            return False
