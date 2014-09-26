# -*- coding: utf-8 -*-

"""
    Clase de servidor del bot.
    Aqui se cargan los modulos de servidor, los handlers, etc.
"""
import json
import logging
from .irc import client


class Server:
    config = None
    sid = None
    pycobot = None
    logger = None
    connection = None

    def __init__(self, pycobot, sid):
        self.logger = logging.getLogger('pyCoBot-' + sid)
        self.config = pycobot.config
        self.pycobot = pycobot
        self.sid = sid
        
        self.connection = client.IRCClient(sid)
        
        sconf = self.config.get("servers.{0}".format(sid))
        self.connection.configure(sconf['host'], sconf['port'], sconf['nick'])

    def connect(self):
        self.logger.info("Conectando...")
        self.connection.connect()

    def readConf(self, key, chan=None, default=""):
        """Lee configuraciones. (Formato: key1.key2.asd)"""
        key = key.replace("network", "irc." + str(self.sid))
        if chan is not None:
            key = key.replace("channel.", "irc." + str(self.sid) + ".channels."
                                                        + chan.lower() + ".")
            if key == "channel":
                key = "irc." + str(self.sid) + ".channels." + chan.lower()
        return self.config.get(key, default)

    def writeConf(self, key, value, chan=None):
        key = key.replace("network", "irc." + str(self.sid))
        if chan is not None:
            key = key.replace("channel.", "irc." + str(self.sid) + ".channels."
                                                        + chan.lower() + ".")
        # D:!!

        try:
            value2 = value.replace("'", "\"")
            value = json.loads(value2)
        except:
            pass
        self.config.put(key, value)
        dump = self.config.export('json', indent=4)
        open("pycobot.conf", "w").write(dump)
        return True
