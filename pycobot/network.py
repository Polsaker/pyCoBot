# -*- coding: utf-8 -*-

"""
    Clase de servidor del bot.
    Aqui se cargan los modulos de servidor, los handlers, etc.
"""
import json
import logging
from .irc import client
from .database import Settings
from .database import User
from .database import UserPriv
import imp
import sys
import inspect
import ast
import pycobot
import builtins
import traceback
import hashlib

class Server:
    config = None  # Kaptan instance
    sid = None  # Server ID (name in the config)
    pycobot = None  # Parent pyCoBot instance (from pycobot.py)
    logger = None
    connection = None # Instance of the IRC client

    modules = {}  # Loaded modules
    handlers = {}  # Registered handlers
    commands = {}  # Registered commands
    configs = {}  # Configuration value definitions
    
    users = {} # Identified users
    
    _rhandlers = []  # :(
    def __init__(self, pycobot, sid):
        self.logger = logging.getLogger('pyCoBot-' + sid)
        self.config = pycobot.config
        self.pycobot = pycobot
        self.sid = sid
        self.configs = json.loads(open("pycobot/configs.json", 'r').read())

        self.connection = client.IRCClient(sid)
        self.connection.addhandler("privmsg", self._processCommands)
        self.connection.addhandler("pubmsg", self._processCommands)

        sconf = self.config.get("servers.{0}".format(sid))
        self.connection.configure(sconf['host'], sconf['port'], sconf['nick'])
        
        self.connection.addhandler("welcome", self._autojoin)

    def connect(self):
        self.logger.info("Conectando...")
        for i in self.getSetting("modules"):
            self.loadModule(i)

        self.connection.connect()
        
    def _processCommands(self, conn, event):
        command = None
        if event.type == "privmsg":
            command = event.splitd[0]
            del event.splitd[0]
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
            self._auth(event)
        elif command == "help" or command == "ayuda": # TODO: command i18n?
            self._help(event)
            return
            
        try:
            self.commands[command]
        except:
            return # 404 command not found
        
        if self.commands[command]['privs'] != '':
            # TODO: More specific channel privileges
            if self._checkprivs(event, self.commands[command]['privs'], event.target, self.commands[command]['module']) is False:
                self.msg(event.target, self._("\00304Error\003: You're not authorized to use this command"))
                return
            
        if self.commands[command]['pparam'] is not None:
            if client.is_channel(event.splitd[self.commands[command]['pparam'] + 1]):
                channel = event.splitd[self.commands[command]['pparam'] + 1]
            else:
                if event.type == "pubmsg":
                    channel = event.target
                else:
                    channel = None
        
        # Call the function
        self.commands[command]['func'](self, self.connection, event)
    
    def _checkprivs(self, ev, privs, chan="*", module="*"):
        try:
            self.users[ev.source.userhost]
            if privs == 0:
                return True
        except:
            return False
        
        for privset in self.users[ev.source.userhost]:
            if privset['priv'] >= privs and (privset['channel'] == chan or privset['channel'] == "*") \
                and (privset['module'] == module or privset['module'] == "*"):
                    return True
        
        return False
    
    # auth command
    def _auth(self, event):
        if event.type == "pubmsg":
            self.msg(event.target, self._("This command must be used via private messages. Try \002/msg {0} auth <user> <password>".format(self.connection.nickname)))
            return
        
        if len(event.splitd) < 2:
            self.msg(event.target, self._("Not enough parameters. Try \002auth <user> <password>"))
            return
        
        passwd = hashlib.sha256(event.splitd[1].encode()).hexdigest()
        try:
            u = User.get(User.username == event.splitd[0], User.password == passwd)
            self.msg(event.target, self._("Successfully logged in"))
            self.users[event.source.userhost] = []
        except:
            self.msg(event.target, self._("Invalid user/password"))
            return
        
        pu = UserPriv.select().where(UserPriv.uid == u.id)
        for priv in pu:
            self.users[event.source.userhost].append({'module': priv.module, 'priv': priv.priv, 'channel': priv.channel})
    
    # Help command
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
                    self.msg(event.target, self._("Help of \002{0}\002 (Alias of \002{1}\002): {2}").format(event.splitd[0], a, self._(chelp)))
                except:
                    self.msg(event.target, self._("Help of \002{0}\002: {1}").format(event.splitd[0], self._(chelp)))
        except IndexError:
            # List all the commands
            comms = ['help', 'auth']
            for i in self.commands:
                comms.append(i)
            comms.sort()
            self.msg(event.target, self._("\002CoBot {0} ({1})\002. The "
                            "command prefix is \002{2}\002.", event.target).format(
                                    pycobot.VERSION, pycobot.CODENAME, self.getSetting("prefix", event.target, self.connection.nickname + ", ", returnfirstitem=True)))
            self.msg(event.target, self._("Commands: {0}", event.target).format(" ".join(comms)))
        
    # Function to send a PRIVMSG/NOTICE using the bot settings
    # --->   USE THIS FUNCTION AND NOT client.privmsg OR     <---
    # --->   client.notice UNLESS IT IS EXTREMELY NECESSARY. <---
    def msg(self, target, message):
        if self.getSetting("nonotice", target, False) is True:
            self.connection.privmsg(target, message)
        else:
            self.connection.notice(target, message)
            
    def _autojoin(self, conn, event):
        for chan in self.getSetting("autojoin"):
            conn.join(chan)
    
    def _(self, string, channel=None):
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
        self.logger.info("Loading local module {0}".format(ModuleName))
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
            self.logger.warning("Tried to load a non-existent module {0}".format(ModuleName))
            return -1  # Meep, the module is not there
        del modulesa
        
        try:
            # Get the module's file
            p = getattr(p, "{0}".format(ModuleName))
            p._ = self._
        except ImportError:
            self.logger.warning("Can't find the main class for module {0}".format(ModuleName))
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
        
        # Load configuration definitions
        try:
            configs = json.loads(open("modules/{0}/configs.json".format(ModuleName), 'r').read())
            self.configs = dict(list(self.configs.items()) + list(configs.items()))
        except:
            pass  # Meh
        
        # Load all the (command)handlers
        funcs = inspect.getmembers(p, predicate=inspect.isfunction)
        for func in funcs:
            try:
                # YAY! We found a command handler there
                self.logger.debug("Found commandhandler {0} in {1}".format(func[1].iamachandler, ModuleName))
                self.registerCommand(func[1].iamachandler, getattr(self.modules[ModuleName], func[1].__name__), ModuleName,
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
                            'module': module,
                            'help': chelp,
                            'privs': privs,
                            'alias': alias,
                            'pparam': privsparameter
                        }
        for i in alias:
            self.commands[i] = {
                            'func': func,
                            'module': module,
                            'help': chelp,
                            'privs': privs,
                            'pparam': privsparameter,
                            'aliasof': command
                        }
    
    def getSetting(self, key, channel=None, default=None, returnfirstitem=False):
        config = {}
        config['scope'] = "channel"
        config['type'] = "str"
        config['concatenate'] = False
        try:
            config = dict(list(config.items()) + list(self.configs[key].items()))
        except KeyError:
            self.logger.warning("Trying to read undefined configuration value {0}, using default settings".format(key))
        resl = []
        # 1 - Try to read channel config
        if channel is not None and config['scope'] == "channel":
            try:
                #s = Settings.get(Settings.channel == channel, Settings.network == self.sid,
                #    Settings.type == "channel", Settings.name == key)
                s = self.pycobot.getSettingFromCache("channel", key, self.sid, channel)
                try:
                    s = ast.literal_eval(s)
                except:
                    pass
                if type(s) != getattr(builtins, config['type']):
                    self.logger.warning("Channel config {0} (Channel: {1}) has the wrong type, expected '{2}', got '{3}'".format(
                                        key, channel, config['type'], type(s)))
                if type(s) == 'list' and config['concatenate'] is True:
                    resl = resl + s 
                else:
                    if not returnfirstitem:
                        return s 
                    else:
                        return s[0]
            except:
                pass
        # 2 - Try to read network config
        if config['scope'] != "global": 
            try:
                #s = Settings.get(Settings.network == self.sid,
                #        Settings.type == "network", Settings.name == key)
                s = self.pycobot.getSettingFromCache("network", key, self.sid)
                try:
                    s = ast.literal_eval(s)
                except:
                    pass
                if type(s) != getattr(builtins, config['type']):
                    self.logger.warning("Network config {0} has the wrong type, expected '{1}', got '{2}'".format(
                                        key, config['type'], type(s)))
                if type(s) == 'list' and config['concatenate'] is True:
                    resl = resl + s 
                else:
                    if not returnfirstitem:
                        return s 
                    else:
                        return s[0] 
            except:
                pass
        # 3 - Try to read the global config
        try:
            #s = Settings.get(Settings.type == "global", Settings.name == key)
            s = self.pycobot.getSettingFromCache("global", key)
            try:
                s = ast.literal_eval(s)
            except:
                pass
            if type(s) != getattr(builtins, config['type']):
                self.logger.warning("Global config {0} has the wrong type, expected '{1}', got '{2}'".format(
                                    key, config['type'], type(s)))
            if type(s) == 'list' and config['concatenate'] is True:
                resl = resl + s 
            else:
                if not returnfirstitem:
                    return s 
                else:
                    return s[0]
        except:
            pass
        
        # 4 - Try to read the config from the file
        try:
            
            value = self.config.get("servers.{0}.{1}".format(self.sid, key))
            if type(value) != getattr(builtins, config['type']):
                self.logger.warning("Config from the file (key: {0}) has the wrong type, expected '{1}', got '{2}'".format(
                                    key, config['type'], type(value)))
            if type(value) == 'list' and config['concatenate'] is True:
                resl = resl + value 
            else:
                 return value 
        except KeyError:
            if default is None:
                return config['default']
            else:
                return default

        return resl
                            
        

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
                except:
                    self.logger.error("Exception when calling handler"
                        " for module '{0}' (event: '{1}'): {2}".format(
                        module, event.type, traceback.format_exc()))
