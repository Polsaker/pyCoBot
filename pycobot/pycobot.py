# -*- coding: utf-8 -*-

"""
    Clase multi-red del bot.
    Aqui se registran los modulos globales.
"""
from .network import Server
import logging
import time

logger = logging.getLogger('pyCoBot')


class pyCoBot:
    servers = {}
    config = None
    daemon = None
    donotdie = False

    def __init__(self, daemon):
        logger.info("Iniciando.")
        self.config = daemon.config
        self.daemon = daemon

        # Registramos los servidores...
        for i in self.config.get("servers"):
            logger.debug("Iniciando servidor '{0}'.".format(i))
            self.servers[i] = Server(self, i)

    def run(self):
        for i in self.servers:
            self.servers[i].connect()

        # :D
        alive = True
        while alive or self.donotdie:
            time.sleep(0.01)  # Grooo!