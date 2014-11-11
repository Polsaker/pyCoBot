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
import inspect


class Server:
    config = None
    sid = None
    pycobot = None
    logger = None
    connection = None

    modules = {}
    handlers = {}
    _rhandlers = []  # :(
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
            return -3  # Meep, the module is loaded
        except KeyError:
            pass
        
        try:
            modulesa = __import__("modules.{0}.{0}".format(ModuleName))
            # Get the module
            p = getattr(modulesa, "{0}".format(ModuleName))
        except ImportError:
            return -1  # Meep, the module is not there
        del modulesa
        
        try:
            # Get the module's file
            p = getattr(p, "{0}".format(ModuleName))
        except ImportError:
            return -2  # Meep, There is no module file
        
        try:
            # Get the module class
            p = getattr(p, "{0}".format(ModuleName))
        except:
            return -5  # Meep, the class doesn't exist
            
        # "Register" and init the module
        try:
            self.modules[ModuleName] = p(self)
        except Exception as e:
            self.logger.warning("Exception loading module {0}: {1}".format(
                    ModuleName, e))
            return -4  # Meep, error calling the class
        
        # Load all the (command)handlers
        funcs = inspect.getmembers(p, predicate=inspect.isfunction)
        for func in funcs:
            try:
                # YAY! We found a command handler there
                func.iamachandler
                pass  # TODO
            except AttributeError:
                pass
            
            try:
                # YAY! We found a regular and boring handler here
                self.registerHandler(func.iamahandler, ModuleName, func)
            except AttributeError:
                pass

    # Register a handler to be proxied
    # !!!! REGISTER YOUR HANDLERS HERE IF YOU DO WITHOUT DECORATORS !!!!
    # (Because if you do it here it will be automagically deleted when
    # the module is unloaded)
    def registerHandler(self, action, module, function):
        if not action in self._rhandlers:
            self.connection.addhandler(action, proxyHandler)
            self._rhandlers.append(action)
        try:
            self.handlers[module]
        except:
            self.handlers[module] = {}
            
        try:
            self.handlers[module][action]
        except:
            self.handlers[module][action] = []
            
        self.handlers[module][action].append(function)
        
        
    # Proxies a handler
    # IRC lib => Server class => Module
    # Bcoz having total control over everything is awesome
    def proxyHandler(self, handler, module):
        pass # TODO

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
