# -*- coding: utf-8 -*-
import urllib.request
import json
import logging
import pprint
import hashlib


class pyCoUpdater:

    def __init__(self, cli, ev):
        self.cli = cli
        self.ev = ev
        self.githttpupd = {}
        self.upd = False

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
        return self.upd

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
                print("------------007")
                for x, xval in enumerate(index['modules']):
                    print("------------008")
                    if val == xval:
                        if self.processgithttp(i, val) is True:
                            self.upd = True

    def processgithttp(self, repo, module):
        response = urllib.request.urlopen('https://github.com/%s/raw' % (repo) +
        '/master/modules/%s/%s.py' % (module, module)).read()
        f = open("modules/%s/%s.py" % (module, module))
        fh = hashlib.sha1(f.read().encode('utf-8')).hexdigest()
        f.close()
        oh = hashlib.sha1(response).hexdigest()
        if not fh == oh:
            logging.info("Actualizando %s. Hash local: %s. Hash remoto: %s" % (
             module, fh, oh))
            self.cli.privmsg(self.ev.target, "\2Actualizando \00303%s" % module)
            f = open("modules/%s/%s.py" % (module, module), "w")
            f.write(response)
            f.close()
            return True
        else:
            return False
