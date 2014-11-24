# -*- coding: utf-8 -*-

"""
    Clase de servidor del bot.
    Aqui se cargan los modulos de servidor, los handlers, etc.
"""
import json
import logging
from .irc import client
from .database import Settings
import imp
import sys
import inspect
import ast

class Server:
    config = None
    sid = None
    pycobot = None
    logger = None
    connection = None

    modules = {}
    handlers = {}
    commands = {}
    
    _rhandlers = []  # :(
    def __init__(self, pycobot, sid):
        self.logger = logging.getLogger('pyCoBot-' + sid)
        self.config = pycobot.config
        self.pycobot = pycobot
        self.sid = sid

        self.connection = client.IRCClient(sid)
        self.connection.addhandler("privmsg", self._processCommands)
        self.connection.addhandler("pubmsg", self._processCommands)

        sconf = self.config.get("servers.{0}".format(sid))
        self.connection.configure(sconf['host'], sconf['port'], sconf['nick'])
        
        self.connection.addhandler("welcome", self._autojoin)

    def connect(self):
        self.logger.info("Conectando...")
        print(self.loadModule("example")) # TODO: Read the config file/database for modules

        self.connection.connect()
        
    def _processCommands(self, conn, event):
        command = None
        if event.type == "privmsg":
            cmd = event.splitd[0]
        else:
            try:
                prefix = self.getSetting("prefix", event.source)
            except:
                pass  # No prefix ?!?!?!
            
            if type(prefix) is list:
                for i in prefix: # :(
                    if event.splitd[0][:len(i)] == i:
                        command = event.splitd[0][len(i):]
                        break
            else:
                if event.splitd[0][:len(prefix)] == i:
                    command = event.splitd[0][len(prefix):]
        
        if not command:
            return
        
        # Valid order prefix for the bot! Check if the command exists
        if command == "auth" or command == "id" or command == "identify":
            # TODO: Core command 'auth'
            return
        elif command == "help" or command == "ayuda": # TODO: command i18n?
            # TODO: help command
            return
            
        try:
            self.commands[command]
        except:
            return # 404 command not found
        
        if self.commands[command]['privs'] != 0:
            # TODO: Command privilege system
            return
        
        # Call the function
        self.commands[command]['func'](self, self.connection, event)
        
    def _autojoin(self, conn, event):
        # TODO: Also read the database for autojoins
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
                self.registerCommand(func[1].iamachandler, func[1], ModuleName,
                        func[1].chelp, func[1].cprivs, func[1].calias)
            except AttributeError:
                pass
            
            try:
                # YAY! We found a regular and boring handler here
                self.registerHandler(func[1].iamahandler, ModuleName, func[1])
            except AttributeError:
                pass
    
    # Register a command with the bot
    def registerCommand(self, command, func, module, chelp='', privs=0, alias=[]):
        self.commands[command] = {
                            'func': func,
                            'help': chelp,
                            'privs': privs,
                            'alias': alias
                        }
        # TODO: Make commands work
        # TODO: Finish user/privs system to make commands work
    
    def getSetting(self, key, channel=None):
        # 1 - Try to read channel config
        if channel is not "1":
            try:
                s = Settings.get(Settings.channel == channel, Settings.network == self.sid,
                    Settings.type == "channel", Settings.name == key)
                try:
                    s = ast.literal_eval(s.value)
                except:
                    pass
                return s.value
            except:
                pass
        # 2 - Try to read network config
        try:
            s = Settings.get(Settings.network == self.sid,
                    Settings.type == "network", Settings.name == key)
            try:
                s = ast.literal_eval(s.value)
            except:
                pass
            return s.value
        except:
            pass
        # 3 - Try to read the global config
        try:
            s = Settings.get(Settings.type == "global", Settings.name == key)
            try:
                s = ast.literal_eval(s.value)
            except:
                pass
            return s.value
        except:
            pass
        
        # 4 - Try to read the config from the file
        try:
            self.config.get("servers.{0}.{1}".format(self.sid, key))
        except:
            raise  # Whoops! value not found
                            
        

    # Register a handler to be proxied
    # !!!! REGISTER YOUR HANDLERS HERE IF YOU DO WITHOUT DECORATORS !!!!
    # (Because if you do it here it will be automagically deleted when
    # the module is unloaded)
    def registerHandler(self, action, module, function):
        if not action in self._rhandlers:
            self.connection.addhandler(action, self.proxyHandler)
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
    def proxyHandler(self, cli, event):
        for module in self.handlers:
            try:
                self.handlers[module][event.type]
            except AttributeError:
                continue
            for handler in self.handlers[module][event.type]:
                try:
                    handler(self.modules[module], self, cli, event)
                except Exception as e:
                    self.logger.warning("Exception when calling handler"
                        " for module '{0}' (event: '{1}'): {2}".format(
                        module, event.type, e))


    # Deprecated!
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
