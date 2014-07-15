# -*- coding: utf-8 -*-
import logging


class IRCClient:
    # Defaults..
    server = None    # Dirección del servidor IRC
    port = 6667      # Puerto al que se conectará
    nick = "Groo"    # Nick
    ident = nick
    gecos = "_"      # "Nombre real"
    ssl = False
    msgdelay = 0.5   # Demora en el envío de mensajes (para no caer por flood)
    reconnects = 10  # Intentos de reconectarse desde la ultima conexion fallida

    connected = False
    logger = None

    def __init__(self, sid):
        self.logger = logging.getLogger('bearded-potato-' + sid)

    def configure(self, server=server, port=port, nick=nick, ident=nick,
                gecos=gecos, ssl=ssl, msgdelay=msgdelay, reconnects=reconnects):
        self.server = server
        self.port = port
        self.nick = nick
        self.ident = ident
        self.gecos = gecos
        self.ssl = ssl
        self.msgdelay = msgdelay

    def connect(self):
        """ Connects to the IRC server. """
        self.logger.info("Conectando a {0}:{1}".format(self.server, self.port))

    def addhandler(self, numeric, function):
        pass