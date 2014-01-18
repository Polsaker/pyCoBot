#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging, re, sys, time

import oyoyo.client
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
import json
import pprint

servers = {}
modules = {}
conf = {}

class NativeHandler(DefaultCommandHandler):
    def __init__(self, cli):
        self.client = cli
        try:
            self.handlers
            self.commandhandlers
        except:
            self.handlers = {}
            self.commandhandlers = {}
        
        self.handlers[cli.host] = []
        self.commandhandlers[cli.host] = {}
        for i, val in enumerate(servers[cli.host]['modules']):
            self.loadmod(servers[cli.host]['modules'][i], cli)

    def handler(self, server, numeric, *kw):
        for i, val in enumerate(self.handlers[server]):
            if self.handlers[server][i]['numeric'] == numeric:
                getattr(self.handlers[server][i]['mod'], self.handlers[server][i]['func'])(self.client, server, *kw)

    def addHandler(self, server, numeric, modulo, func):
        h = {}
        h['numeric'] = numeric
        h['mod'] = modulo
        h['func'] = func
        self.handlers[server].append(h)

    def addCommandHandler(self, server, command, module, func):
        h = {}
        h['mod'] = module
        h['func'] = func
        self.commandhandlers[server][command] = h

    # autojoin
    def welcome(self, server, *kw):
        for i, val in enumerate(servers[server]['autojoin']):
            helpers.join(self.client,servers[server]['autojoin'][i])

    def privmsg(self, server, nick, chan, msg):
        p = re.compile("(?:"+re.escape(servers[server]['prefix'])+"|"+re.escape(servers[server]['nick'])+"[:, ]? )(.*)(?!\w+)")
        m = p.search(msg)
        if not m == None:
            com = m.group(1)
            try:
                self.commandhandlers[server][com]
                getattr(self.commandhandlers[server][com]['mod'], self.commandhandlers[server][com]['func'])(self.client, server, nick, chan, msg)
            except NameError:
                pass
    # carga de modulos
    def loadmod(self, module, cli):
        logging.info('Cargando modulo "%s" en %s' % (module, cli.host))
        try:
            # D:
            modulef = open('modules/%s/%s.py' % (module, module)).read()
            nclassname = "m" + str(int(time.time())) + "x" + module
            mod = re.sub(r".*class (.*):", "class " + nclassname + ":", modulef)
            open('tmp/%s.py' % module, 'w').write(mod)

            modules[cli.host] = {}
            modules[cli.host][module] = {}
            modules[cli.host][module]['importd'] = __import__("tmp." + module, fromlist=[nclassname])
            modules[cli.host][module]['mainclass'] = nclassname
            modules[cli.host][module]['module'] = my_import("tmp."+module+"."+nclassname)(self, cli)

        except IOError:
            logging.error("No se pudo cargar el modulo '%s'. No se ha encontrado el archivo." % module)

def my_import(cl):
        d = cl.rfind(".")
        classname = cl[d+1:len(cl)]
        m = __import__(cl[0:d], globals(), locals(), [classname])
        return getattr(m, classname)

def main():
        logging.basicConfig(level=logging.DEBUG) # Logging
        try:
            jsonConf = open("pycobot.conf").read()
        except IOError:
            logging.error('No se ha podido abrir el archivo de configuración')
            sys.exit("Missing config file!")


        conf = json.loads(jsonConf)
        ircapp = oyoyo.client.IRCApp()

        # Cargamos los servidores...
        for i, val in enumerate(conf['irc']):
            servers[conf['irc'][i]['server']] =conf['irc'][i]
            servers[conf['irc'][i]['server']]['client'] = oyoyo.client.IRCClient(NativeHandler, host=conf['irc'][i]['server'], port=conf['irc'][i]['port'],
            nick=conf['irc'][i]['nick'])
            ircapp.addClient(servers[conf['irc'][i]['server']]['client'])	

        ircapp.run() # Comenzamos a conectar y a procesar..

if __name__ == '__main__':
    main()
