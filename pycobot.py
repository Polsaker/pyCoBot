#!/usr/bin/python
# -*- coding: utf-8 -*-

import irc.client
from irc import events
import sys, json, logging, re, time
from pprint import pprint
# Variables globales:
conf = {} # Configuración
servers = {} # Servidores
modules = {} # Módulos
handlers = {} # 
commandhandlers = {} # 

client = None

_rfc_1459_command_regexp = re.compile("^(:(?P<prefix>[^ ]+) +)?(?P<command>[^ ]+)( *(?P<argument> .+))?")
class pyCoBot:
    def __init__(self, server, client, conf):
        handlers[server] = []
        self.server = client.server()
        self.server.connect(server, conf['port'], conf['nick'],
            username = conf['nick'], ircname = "pyCoBot")
        self.server.add_global_handler("all_raw_messages", self.allraw)
        servers[server] = conf
        servers[server]['servobj'] = server  
        modules[server] = {}
        
        self.conf = conf
        
        for i, val in enumerate(conf['modules']):
            loadmod(conf['modules'][i], self.server, conf['server'], self)
        
    
    def allraw(self, con, event):
        ev = self.processline(event.arguments[0], con) 
        for i, val in enumerate(handlers[self.conf['server']]): # TODO: hacer esto es feo, cambiarlo por algo mejor!
            if ev.type == handlers[self.conf['server']][i]['numeric']:
                getattr(handlers[self.conf['server']][i]['mod'], handlers[self.conf['server']][i]['func'])(self.conf['server'], self.server)
        
        if ev.type == "welcome":
            for i, val in enumerate(servers[event.realserv]['autojoin']):
                con.join(servers[event.realserv]['autojoin'][i])

    # Procesa una linea y retorna un Event
    def processline(self, line, c):
        prefix = None
        command = None
        arguments = None

        m = _rfc_1459_command_regexp.match(line)
        if m.group("prefix"):
            prefix = m.group("prefix")

        if m.group("command"):
            command = m.group("command").lower()

        if m.group("argument"):
            a = m.group("argument").split(" :", 1)
            arguments = a[0].split()
            if len(a) == 2:
                arguments.append(a[1])

        # Translate numerics into more readable strings.
        command = events.numeric.get(command, command)

        if command in ["privmsg", "notice"]:
            target, message = arguments[0], arguments[1]
            messages = irc.client._ctcp_dequote(message)

            if command == "privmsg":
                if irc.client.is_channel(target):
                    command = "pubmsg"
            else:
                if irc.client.is_channel(target):
                    command = "pubnotice"
                else:
                    command = "privnotice"

            for m in messages:
                if isinstance(m, tuple):
                    if command in ["privmsg", "pubmsg"]:
                        command = "ctcp"
                    else:
                        command = "ctcpreply"

                    if command == "ctcp" and m[0] == "ACTION":
                        return irc.client.Event("action", prefix, target, m[1:])
                    else:
                        return irc.client.Event(command, irc.client.NickMask(prefix), target, m)
                else:
                    return irc.client.Event(command, irc.client.NickMask(prefix), target, [m])
        else:
            target = None

            if command == "quit":
                arguments = [arguments[0]]
            elif command == "ping":
                target = arguments[0]
            else:
                target = arguments[0]
                arguments = arguments[1:]

            if command == "mode":
                if not is_channel(target):
                    command = "umode"

            return irc.client.Event(command, prefix, target, arguments)
        

    def addHandler(self, server, numeric, modulo, func):
        """ Registra un handler con el bot.
        Parametros:
            - server: Nombre (dirección) del servidor en el que se registra el handler (la misma
            que aparece en la configuración)
            - numeric: Nombre del comando IRC que accionara el handler (lista: irc/events.py)
            - modulo: 'self' del módulo en el que se registra el handler
            - func: la función que se llamará en el módulo en cuestión
        """
        h = {}
        h['numeric'] = numeric
        h['mod'] = modulo
        h['func'] = func

        handlers[server].append(h)
        logging.debug("Registrado handler en '%s' ('%s')" % (server, numeric))

# carga de modulos
def loadmod(module, cli, server, bot):
    logging.info('Cargando modulo "%s" en %s' % (module, server))
    try:
        # D:
        modulef = open('modules/%s/%s.py' % (module, module)).read()
        nclassname = "m" + str(int(time.time())) + "x" + module
        mod = re.sub(r".*class (.*):", "class " + nclassname + ":", modulef)
        open('tmp/%s.py' % module, 'w').write(mod)

        modules[server][module] = my_import("tmp."+module+"."+nclassname)(server, bot, cli)

    except IOError:
        logging.error("No se pudo cargar el modulo '%s'. No se ha encontrado el archivo." % module)

def main():
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        jsonConf = open("pycobot.conf").read()
    except IOError:
        logging.error('No se ha podido abrir el archivo de configuración')
        sys.exit("Missing config file!")

    conf = json.loads(jsonConf) # Cargar la configuración
    
    client= irc.client.IRC()
    
    # Añadir servidores
    for i, val in enumerate(conf['irc']):
        pycobot = pyCoBot(conf['irc'][i]['server'], client, conf['irc'][i])
        """handlers[conf['irc'][i]['server']] = []
        server = client.server()
        server.connect(conf['irc'][i]['server'], conf['irc'][i]['port'],
        conf['irc'][i]['nick'], username = conf['irc'][i]['nick'], ircname = "pyCoBot")
        server.add_global_handler("all_raw_messages", allraw)
        servers[conf['irc'][i]['server']] = conf['irc'][i]   
        servers[conf['irc'][i]['server']]['servobj'] = server  
        modules[conf['irc'][i]['server']] = {}
        
        pprint(handlers)
        commandhandlers[conf['irc'][i]['server']] = {} 
        
        for i, val in enumerate(conf['irc'][i]['modules']):
            loadmod(conf['irc'][i]['modules'][i], server, conf['irc'][i]['server']) """
        
        
    client.process_forever()

def my_import(cl):
        d = cl.rfind(".")
        classname = cl[d+1:len(cl)]
        m = __import__(cl[0:d], globals(), locals(), [classname])
        return getattr(m, classname)
if __name__ == "__main__":
    main()
