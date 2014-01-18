#!/usr/bin/python
import logging
import re
import time

import oyoyo.client
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
import json
import pprint

servers = {}

class NativeHandler(DefaultCommandHandler):
	def n001(self, server, nick, chan, msg):
		for i, val in enumerate(servers[server]['autojoin']):
			
			helpers.join(self.client,servers[server]['autojoin'][i])
	

def main():
	logging.basicConfig(level=logging.DEBUG) # Logging
	
	jsonConf = open("pycobot.conf").read()
	conf = json.loads(jsonConf)
	
	ircapp = oyoyo.client.IRCApp()
	
	for i, val in enumerate(conf['irc']):
		servers[conf['irc'][i]['server']] =conf['irc'][i]
		servers[conf['irc'][i]['server']]['client'] = oyoyo.client.IRCClient(NativeHandler, host=conf['irc'][i]['server'], port=conf['irc'][i]['port'],
		nick=conf['irc'][i]['nick'])
		ircapp.addClient(servers[conf['irc'][i]['server']]['client'])
		
	ircapp.run()
	

#	cli = IRCClient(NativeHandler, host=HOST, port=PORT, nick=NICK,
#	connect_cb=connect_cb)
#	conn = cli.connect() # Conexión
#
#	while True:
#		time.sleep(0.1) # pa' que no use toda la cpu!
#		next(conn)


if __name__ == '__main__':
	main()
