# -*- coding: utf-8 -*-
import re
from irc import events
import irc.client
import time
import hashlib
import logging
import os
import json
import _thread
import sys
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import updater
import pprint
_rfc_1459_command_regexp = re.compile("^(:(?P<prefix>[^ ]+) +)?" +
    "(?P<command>[^ ]+)( *(?P<argument> .+))?")

engine = create_engine("sqlite:///db/cobot.db")
Base = declarative_base()

from .tables import User, UserPriv

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


class pyCoBot:
    def __init__(self, server, client, conf):
        self.session = Session
        self.botcli = client
        self.handlers = []
        self.server = client.server()
        self.server.connect(server, conf['port'], conf['nick'],
            username=conf['nick'], ircname="pyCoBot")
        self.server.add_global_handler("all_raw_messages", self.allraw)

        self.modules = {}
        self.modinfo = {}
        self.modname = {}
        self.commandhandlers = {}
        self.conf = conf
        self.authd = {}  # Usuarios autenticados..
        for i, val in enumerate(conf['modules']):
            self.loadmod(conf['modules'][i], conf['server'])

    def allraw(self, con, event):
        ev = self.processline(event.arguments[0], con)
        # OPTIMIZE: hacer esto es feo, cambiarlo por algo mejor!
        for i, val in enumerate(self.handlers):
            if ev.type == self.handlers[i]['numeric']:
                m = getattr(self.handlers[i]['mod'], self.handlers[i]['func'])
                m(self.server)

        if ev.type == "privmsg" or ev.type == "pubmsg":
            #p = re.compile("(?:" + re.escape(self.conf['prefix']) + "|" +
            #    re.escape(self.conf['nick']) + "[:, ]? )(.*)(?!\w+)")
            # Buscamos por el prefijo..
            p1 = re.compile(re.escape(self.conf['prefix']) +
                "(\S{1,52})[ ]?(.*)")
            m1 = p1.search(ev.arguments[0])

            # Buscamos por el nick como prefijo..
            p2 = re.compile(re.escape(self.conf['nick']) +
                "[:, ]? (\S{1,52})[ ]?(.*)")
            m2 = p2.search(ev.arguments[0])
            if not m1 is None:
                del ev.splitd[0]
                com = m1.group(1)
            elif not m2 is None:
                del ev.splitd[0]
                del ev.splitd[0]
                com = m2.group(1)

            if not m1 is None or not m2 is None:
                if com == "help" or com == "ayuda":
                    r = False
                    if not len(ev.splitd) > 0:
                        comlist = "help auth "
                        for i in list(self.commandhandlers.keys()):
                            if self.authchk(ev.source, self.commandhandlers[i]
                             ['cpriv'], self.modname[self.commandhandlers[i]
                             ['mod']], ev.target) is True:
                                comlist = comlist + i + " "

                        con.privmsg(ev.target, "\2pyCoBot alpha\2. Comandos " +
                        "empezar con \2" + self.conf["prefix"] + "\2. " +
                        "Escriba " + self.conf["prefix"] + "help \2<comando>" +
                        "\2 para mas información sobre un comando")

                        con.privmsg(ev.target, "Comandos: " + comlist)
                    else:
                        if ev.splitd[0] == "help":  # Harcoded help :P
                            r = "Muestra la ayuda de un comando, o, si no " + \
                             " tiene parametros, la lista de comandos." + \
                             " Sintaxis: help [comando]"
                        elif ev.splitd[0] == "auth":
                            r = "Identifica a un usuario registrado con el " + \
                             " Bot. Sintaxis" + \
                             " Sintaxis: help [comando]"
                        else:
                            try:
                                r = self.commandhandlers[ev.splitd[0]]['chelp']
                            except KeyError:
                                pass
                        if not r:
                            con.privmsg(ev.target, "No se ha encontrado el " +
                             "comando")
                        else:
                            con.privmsg(ev.target, "Ayuda de \2" + ev.splitd[0]
                             + "\2: " + r)
                elif com == "auth" and ev.type == "privmsg":
                    self.auth(ev)
                elif com == "update":
                    # >:D
                    _thread.start_new_thread(self.updater, (self.server, ev))
                else:
                    try:
                        self.commandhandlers[com]
                    except KeyError:
                        return 0
                    # Verificación de autenticación
                    try:
                        c = getattr(self.commandhandlers
                         [com]['mod'], com + "_p")(self,
                         self.server, ev)
                    except AttributeError:
                        c = ev.target
                    authd = self.authchk(ev.source, self.commandhandlers[com]
                    ['cpriv'], self.modname[self.commandhandlers[com]['mod']],
                    c)

                    if authd is True:
                        getattr(self.commandhandlers[com]['mod'], self.
                         commandhandlers[com]['func'])(self, self.server, ev)
                    else:
                        self.server.privmsg(ev.target, "\00304Error\003: No a" +
                        "utorizado")

        if ev.type == "welcome":
            for i, val in enumerate(self.conf['autojoin']):
                con.join(self.conf['autojoin'][i])

    def authchk(self, host, cpriv, modsec, chan=False):
        # Verificación de autenticación
        if not cpriv == -1:
            try:
                uid = self.authd[host]
                continua = False
                session = self.session()
                for row in session.query(UserPriv) \
                .filter(UserPriv.uid == uid):
                    if (row.priv >= cpriv) and (row.secmod == "*" or row.secmod
                     == modsec):
                        if chan is False:
                            continua = True
                        else:
                            if row.secchan == "*" or row.secchan == chan:
                                continua = True
            except KeyError:
                return False
            if not continua is True:
                return False
            else:
                return True
        else:
            return True

    def updater(self, cli, event):
        """upd = updater.pyCoUpdater(cli, event)
        for key in list(self.modname.keys()):
            try:
                val = self.modname[key]
                f = open('modules/%s/%s.json' % (val, val))
                j = json.load(f)
                upd.addfile(j['type'], val, user=j['user'], repo=j['repo'],
                 url=j['url'])
            except IOError:
                pass
        if upd.update() is True:"""
        self.restart_program("[UPDATE] Aplicando actualizaciones")

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
                        return irc.client.Event(command,
                             irc.client.NickMask(prefix), target, m)
                else:
                    return irc.client.Event(command,
                         irc.client.NickMask(prefix), target, [m])

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
                if not irc.client.is_channel(target):
                    command = "umode"

            return irc.client.Event(command, prefix, target, arguments)

    def auth(self, event):
        session = self.session()
        passw = hashlib.sha1(event.splitd[1].encode('utf-8')).hexdigest()

        try:
            row = session.query(User).filter(User.name == event.splitd[0]) \
             .filter(User.password == passw).one()
            self.authd[event.source] = row.uid
            self.server.privmsg(event.target, "Autenticado exitosamente como" +
             row.name)
        except:
            self.server.privmsg(event.target, "\00304Error\003: Usuario o " +
            "contraseña incorrectos")

    def addHandler(self, numeric, modulo, func):
        """ Registra un handler con el bot.
        Parametros:
            - server: Nombre (dirección) del servidor en el que se registra el
             handler (la misma que aparece en la configuración)
            - numeric: Nombre del comando IRC que accionara el handler
              (lista: irc/events.py)
            - modulo: 'self' del módulo en el que se registra el handler
            - func: la función que se llamará en el módulo en cuestión
        """
        h = {}
        h['numeric'] = numeric
        h['mod'] = modulo
        h['func'] = func

        self.handlers.append(h)

        logging.debug("Registrado handler en '%s' ('%s')"
           % (self.conf['server'], numeric))

    def addCommandHandler(self, command, module, func, chelp="", cpriv=-1,
         cprivchan=False, privmsgonly=False):
        """ Registra un commandHandler con el bot (un comando, bah)
        Parametros:
            - server: Nombre (dirección) del servidor en el que se registra el
             handler (la misma que aparece en la configuración)
            - command: Nombre del comando que se va a registrar
            - módulo: 'self' del módulo donde se registra el handler
            - fund; la función que se llamara en el módulo en cuestión.
            - chelp: La ayuda del comando
            - cpriv y cprivsect: Privilegios requeridos para usar el comando
            - privmsgonly: si el comando solo debe ser ejecutado por privmsg
        Los comandos se accionan al escribir <prefijo>comando;
         <nickdelbot>, comando; <nickdelbot>: comando y <nickdelbot> comando """
        h = {}
        h['mod'] = module
        h['func'] = func
        h['cpriv'] = cpriv
        h['cprivchan'] = cprivchan
        h['privmsgonly'] = privmsgonly
        h['chelp'] = chelp
        self.commandhandlers[command] = h

        logging.debug("Registrado commandHandler en '%s' ('%s')"
         % (self.conf['server'], command))

    # carga de modulos
    def loadmod(self, module, cli):
        logging.info('Cargando modulo "%s" en %s'
         % (module, self.conf['server']))
        try:
            # D:
            modulef = open('modules/%s/%s.py' % (module, module)).read()
            nclassname = "m" + str(int(time.time())) + "x" + module
            mod = re.sub(r".*class (.*):", "class " + nclassname + ":", modulef)
            open('tmp/%s/%s.py' % (self.conf['pserver'], nclassname),
                 'w').write(mod)

            self.modules[module] = my_import("tmp." + self.conf['pserver'] +
            "." + nclassname + "." + nclassname)(self, cli)
            self.modinfo[module] = nclassname
            self.modname[self.modules[module]] = module
        except IOError:
            logging.error("No se pudo cargar el modulo '%s'. No se ha" +
            " encontrado el archivo." % module)

    def unloadmod(self, module):
        logging.info('Des-cargando modulo "%s" en %s'
         % (module, self.conf['server']))
        try:
            self.modules[module]
        except NameError:
            logging.error("El modulo %s no existe o no esta cargado" % module)
            return 1
        os.remove("tmp/%s/%s.py" % (self.conf['pserver'], self.modinfo[module]))
        # Eliminamos los handlers..
        for i, val in enumerate(self.handlers):
            if self.modules[module] == self.handlers[i]['mod']:
                logging.debug('Eliminando handler "%s" del modulo %s en %s'
                 % (self.handlers[i]['numeric'], module, self.conf['server']))
                del self.handlers[i]

        l = []
        # Eliminamos los commandhandlers
        for i in list(self.commandhandlers.keys()):
            if self.modules[module] == self.commandhandlers[i]['mod']:
                l.append(i)
        for q in enumerate(l):
                logging.debug('Eliminando commandhandler "%s" del modulo %s'
                 % (q[1], module))
                del self.commandhandlers[q[1]]

    def restart_program(self, quitmsg):
        for i in enumerate(self.botcli.boservers):
            i[1].server.quit(quitmsg)
        python = sys.executable
        os.execl(python, python, * sys.argv)


def my_import(cl):
        d = cl.rfind(".")
        classname = cl[d + 1:len(cl)]
        m = __import__(cl[0:d], globals(), locals(), [classname])
        return getattr(m, classname)