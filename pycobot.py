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
		self.handlers = {}
		self.handlers[cli.host] = []
		for i, val in enumerate(servers[cli.host]['modules']):
			self.loadmod(servers[cli.host]['modules'][i], cli)
			
	def handler(self, server, numeric, *kw):
		for i, val in enumerate(self.handlers[server]):
			if self.handlers[server][i]['numeric'] == numeric:
				getattr(modules[servers[server]['client'].host][self.handlers[server][i]['mod']]['module'], self.handlers[server][i]['func'])(self.client, server, *kw)
	
	def addHandler(self, server, numeric, modulo, func):
		h = {}
		h['numeric'] = numeric
		h['mod'] = modulo
		h['func'] = func
		self.handlers[server].append(h)
	
	# autojoin
	def welcome(self, server, *kw):
		print("-------------------------___WTF!")
		for i, val in enumerate(servers[server]['autojoin']):
			helpers.join(self.client,servers[server]['autojoin'][i])
			
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
	

#	cli = IRCClient(NativeHandler, host=HOST, port=PORT, nick=NICK,
#	connect_cb=connect_cb)
#	conn = cli.connect() # Conexión
#
#	while True:
#		time.sleep(0.1) # pa' que no use toda la cpu!
#		next(conn)


if __name__ == '__main__':
	main()
