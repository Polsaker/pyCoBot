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
import pycobot

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
            prefix = None
            try:
                prefix = self.getSetting("prefix", event.target)
            except:
                pass  # No prefix ?!?!?!
            
            if prefix:
                if type(prefix) is list:
                    for i in prefix: # :(
                        if event.splitd[0][:len(i)] == i:
                            command = event.splitd[0][len(i):]
                            del event.splitd[0]
                            break
                else:
                    if event.splitd[0][:len(prefix)] == prefix:
                        command = event.splitd[0][len(prefix):]
                        del event.splitd[0]
            if not command:
                try:
                    if self.connection.nickname in event.splitd[0]:
                        command = event.splitd[1]
                        del event.splitd[0]
                        del event.splitd[0]
                except:
                    pass

        if not command:
            return
        
        
        
        # Valid order prefix for the bot! Check if the command exists
        if command == "auth" or command == "id" or command == "identify":
            # TODO: Core command 'auth'
            return
        elif command == "help" or command == "ayuda": # TODO: command i18n?
            self._help(event)
            return
            
        try:
            self.commands[command]
        except:
            return # 404 command not found
        
        if self.commands[command]['privs'] != 0:
            # TODO: Command privilege system
            if self.commands[command]['pparam'] is not None:
                if client.is_channel(event.splitd[self.commands[command]['pparam'] + 1]):
                    channel = event.splitd[self.commands[command]['pparam'] + 1]
                else:
                    if event.type == "pubmsg":
                        channel = event.target
                    else:
                        channel = None
            return
        
        # Call the function
        self.commands[command]['func'](self, self.connection, event)
    
    # [Internal] Help command
    def _help(self, event):
        try:
            if event.splitd[0] == "":
                raise # :D
            if event.splitd[0] == "help" or event.splitd[0] == "ayuda": 
                self.msg(event.target, self._("Help of \002{0}\002: {1}".format("help", self._("Returns the list of commands or gives the help for a specific command. Usage: help [command]"))))
            elif event.splitd[0] == "auth" or event.splitd[0] == "id" or event.splitd[0] == "identify":
                self.msg(event.target, self._("Help of \002{0}\002: {1}".format("auth", self._("Authenticates a user with the bot. Usage: auth <user> <password>"))))
            else:
                try:
                    chelp = self.commands[event.splitd[0]]['help']
                except:
                    self.msg(event.target, self._("That command doesn't exist or has no help."))
                    return
                try:
                    a = self.commands[event.splitd[0]]['aliasof']
                    self.msg(event.target, self._("Help of \002{0}\002 (Alias of \002{1}\002): {2}").format(event.splitd[0], a, chelp))
                except:
                    self.msg(event.target, self._("Help of \002{0}\002: {1}").format(event.splitd[0], chelp))
        except IndexError:
            # List all the commands
            comms = ['help', 'auth']
            for i in self.commands:
                comms.append(i)
            comms.sort()
            self.msg(event.target, self._("\002CoBot {0} ({1})\002. The "
                            "command prefix is \002{2}\002.", event.target).format(
                                    pycobot.VERSION, pycobot.CODENAME, self.getSetting("prefix", event.target, self.connection.nickname + ", ")))
            self.msg(event.target, self._("Commands: {0}", event.target).format(" ".join(comms)))
        
    # Function to send a PRIVMSG/NOTICE using the bot settings
    # --->   USE THIS FUNCTION AND NOT client.privmsg OR  <---
    # --->   client.notice EXTREMELY NECESSARY.           <---
    def msg(self, target, message):
        if self.getSetting("nonotice", target, False) is True:
            self.connection.privmsg(target, message)
        else:
            self.connection.notice(target, message)
            
    def _autojoin(self, conn, event):
        # TODO: Also read the database for autojoins
        for chan in self.config.get("servers.{0}.autojoin".format(self.sid)):
            conn.join(chan)
    
    def _(self, string, channel=None):
        # TODO: Determine the language and return the translated string
        lang = self.getSetting("language", channel, "en")
        if lang == "en":
            return string
        else:
            try:
                return self.pycobot.daemon.langs[lang][string]
            except:
                return string
            
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
            p._ = self._
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
                        func[1].chelp, func[1].cprivs, func[1].calias, func[1].cprivspar)
            except AttributeError:
                pass
            
            try:
                # YAY! We found a regular and boring handler here
                self.registerHandler(func[1].iamahandler, ModuleName, func[1])
            except AttributeError:
                pass
    
    # Register a command with the bot
    def registerCommand(self, command, func, module, chelp='', privs=0, alias=[], privsparameter=None):
        self.commands[command] = {
                            'func': func,
                            'help': chelp,
                            'privs': privs,
                            'alias': alias,
                            'pparam': privsparameter
                        }
        for i in alias:
            self.commands[i] = {
                            'func': func,
                            'help': chelp,
                            'privs': privs,
                            'pparam': privsparameter,
                            'aliasof': command
                        }
    
    def getSetting(self, key, channel=None, default=None):
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
            
            return self.config.get("servers.{0}.{1}".format(self.sid, key))
        except:
            return default  # Whoops! value not found
                            
        

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
