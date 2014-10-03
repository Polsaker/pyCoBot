# -*- coding: utf-8 -*-

"""
    Clase de servidor del bot.
    Aqui se cargan los modulos de servidor, los handlers, etc.
"""
import json
import logging
from .irc import client
import imp
import sys


class Server:
    config = None
    sid = None
    pycobot = None
    logger = None
    connection = None

    modules = {}
    def __init__(self, pycobot, sid):
        self.logger = logging.getLogger('pyCoBot-' + sid)
        self.config = pycobot.config
        self.pycobot = pycobot
        self.sid = sid

        self.connection = client.IRCClient(sid)

        sconf = self.config.get("servers.{0}".format(sid))
        self.connection.configure(sconf['host'], sconf['port'], sconf['nick'])
        
        self.connection.addhandler("welcome", self._autojoin)

    def connect(self):
        self.logger.info("Conectando...")
        #self.connection.connect()
        print(self.loadModule("example"))
        
    def _autojoin(self, conn, event):
        for chan in self.config.get("servers.{0}.autojoin".format(self.sid)):
            conn.join(chan)
    
    # Loads a module locally.
    # Returns:
    #  -1: Module not found
    #  -2: Module's main file not found
    #  -3: The module is already loaded!
    #  -4: Error loading the module (the class doesn't exist or there is a problem on the __init__?)
    def loadModule(self, ModuleName):
        try:
            # Check if the module is loaded
            self.modules[ModuleName]
            return -3
        except KeyError:
            pass
        
        try:
            modulesa = __import__("modules.{0}.{0}".format(ModuleName))
            # Get the module
            p = getattr(modulesa, "{0}".format(ModuleName))
        except ImportError:
            return -1
        del modulesa
        
        try:
            # Get the module's file
            p = getattr(p, "{0}".format(ModuleName))
        except ImportError:
            return -2

        # "Register" and init the module
        try:
            self.modules[ModuleName] = p(self)
        except Exception as e:
            return -4
    

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
