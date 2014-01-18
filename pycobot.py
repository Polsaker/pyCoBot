#!/usr/bin/python
import logging
import re
import time

from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers

# TODO: Mover esto a una archivo de configuración!!!
HOST = 'irc.freenode.net'
PORT = 6667
NICK = 'pyCoBot-dev'
CHANNEL = '#cobot'


class NativeHandler(DefaultCommandHandler):
	#algo D:
	def privmsg(self, nick, chan, msg):
		print('ALGO D:')


def connect_cb(cli):
	helpers.join(cli, CHANNEL) # Entra a un canal...


def main():
	logging.basicConfig(level=logging.DEBUG) # Logging

	cli = IRCClient(NativeHandler, host=HOST, port=PORT, nick=NICK,
	connect_cb=connect_cb)
	conn = cli.connect() # Conexión

	while True:
		time.sleep(0.1) # pa' que no use toda la cpu!
		next(conn)


if __name__ == '__main__':
	main()
