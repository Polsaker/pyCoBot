# -*- coding: utf-8 -*-
from .network import Server
import logging
import time
import gettext

logger = logging.getLogger('pyCoBot')


class pyCoBot:
    servers = {}
    config = None
    daemon = None
    donotdie = False

    def __init__(self, daemon):
        logger.info("Starting.")
        self.config = daemon.config
        self.daemon = daemon

        for i in self.config.get("servers"):
            logger.debug("Starting server '{0}'.".format(i))
            self.servers[i] = Server(self, i)

    def run(self):
        for i in self.servers:
            self.servers[i].connect()

        # :D
        alive = True
        while alive or self.donotdie:
            time.sleep(1)  # Grooo!
            alive = False
            for i in self.servers:
                if self.servers[i].connection.connected is True or  \
                                     self.servers[i].connection.reconncount <= \
                                          self.servers[i].connection.reconnects:
                    alive = True
