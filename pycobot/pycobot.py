# -*- coding: utf-8 -*-
import re
import time
import hashlib
import logging
import os
import json
import _thread
import sys
import shutil
from peewee import peewee
from . import updater
import pprint

########
VER_MAJOR = "2"
VER_MINOR = "0"
VER_STS = " Alpha"
VER_CODENAME = "Gizkard"
VER_STRING = "%s.%s%s (%s)" % (VER_MAJOR, VER_MINOR, VER_STS, VER_CODENAME)
#######

_rfc_1459_command_regexp = re.compile("^(:(?P<prefix>[^ ]+) +)?" +
    "(?P<command>[^ ]+)( *(?P<argument> .+))?")

database = peewee.SqliteDatabase('db/cobot.db', threadlocals=True)


class BaseModel(peewee.Model):
    class Meta:
        database = database

from .tables import User, UserPriv

try:
    User.create_table()
    UserPriv.create_table()
except:
    pass


class pyCoBot:
    def __init__(self, server, client, conf, mconf, sid):
        # zona de millones de definiciones de variables que se usan y no se usan
        self.sid = sid  # server id aka: el lugar que ocupa en el array de conf.
        self.botcli = client
        try:
            self.botcli.bots
        except:
            self.botcli.bots = []
        self.botcli.bots.append(self)
        self.handlers = []
        self.timehandlers = []
        self.mconf = mconf
        self.server = client.server()
        self.conf = conf
        self.modules = {}
        self.modinfo = {}
        self.modname = {}
        self.commandhandlers = {}
        
        self.authd = {}  # Usuarios autenticados..
        self.server.addhandler("pubmsg", self._cproc)
        self.server.addhandler("privmsg", self._cproc)
        self.server.addhandler("welcome", self._joinchans)
        for i, val in enumerate(conf['modules']):
            self.loadmod(conf['modules'][i], conf['server'])
            
        try:
            self.server.connect(server, conf['port'], conf['nick'],
                conf['nick'], "CoBot/" + VER_STRING)
        except:
            pass  # :P

    def _cproc(self, con, ev):
        p1 = re.compile("^" + re.escape(self.conf['prefix']) +
            "(\S{1,52})[ ]?(.*)", re.IGNORECASE)
        m1 = p1.search(ev.arguments[0])

        # Buscamos por el nick como prefijo..
        p2 = re.compile("^" + re.escape(self.conf['nick']) +
            "[:, ]? (\S{1,52})[ ]?(.*)", re.IGNORECASE)
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
                         ['mod']], ev.target) is True and self. \
                         commandhandlers[i]['alias'] == i:
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
                         " Bot." + "Sintaxis: auth <usuario> <contraseña>" \
                         ". Este comando debe usarse vía mensaje privado."
                    else:
                        pprint.pprint(self.commandhandlers[ev.splitd[0]])
                        try:
                            r = self.commandhandlers[ev.splitd[0]]['chelp']
                            if not self.commandhandlers[ev.splitd[0]][
                            'alias'] != ev.splitd[0]:
                                r = "Alias de " + self.commandhandlers[ev.
                                splitd[0]]['alias'] + " " + r

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
                ocom = self.commandhandlers[com]['alias']
                if self.commandhandlers[com]['privmsgonly'] is True and \
                 ev.type == "pubmsg":
                    return 0
                try:
                    c = getattr(self.commandhandlers
                     [com]['mod'], ocom + "_p")(self,
                     self.server, ev)
                except AttributeError:
                    c = ev.target
                authd = self.authchk(ev.source, self.commandhandlers[com]
                ['cpriv'], self.modname[self.commandhandlers[com]['mod']],
                c)

                if authd is True:
                    getattr(self.commandhandlers[com]['mod'], ocom)(self,
                     self.server, ev)
                else:
                    self.server.privmsg(ev.target, "\00304Error\003: No a" +
                    "utorizado")

        #if ev.type == "welcome":
        #    import pprint
        #    pprint.pprint(self.conf)
        #    for i, val in enumerate(self.conf['autojoin']):
        #        con.join(self.conf['autojoin'][i])
        #elif ev.type == "ping":
        #    con.pong(ev.target)
        #elif ev.type == "ctcp":
        #    if ev.arguments[0] == "VERSION":
        #        con.ctcp_reply(ev.source, "VERSION CoBot/%s" % VER_STRING)
        #    elif ev.arguments[0] == "PING":
        #        con.ctcp_reply(ev.source, "PING " + ev.arguments[1])

    def _joinchans(self, con, ev):
        for i, val in enumerate(self.conf['autojoin']):
            con.join(self.conf['autojoin'][i])

    def authchk(self, host, cpriv, modsec, chan=False):
        # Verificación de autenticación
        if not cpriv == -1:
            try:
                uid = self.authd[host]
                continua = False
                for row in UserPriv.select().where(UserPriv.uid == uid):
                    if (row.priv >= cpriv) and (row.secmod == "*" or row.secmod
                     == modsec):
                        if chan is False and row.secchan == "*":
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
    
    def is_identified(self, host):
        # Verificación de autenticación
        try:
            uid = self.authd[host]
            continua = False
            user = UserPriv.select().where(UserPriv.uid == uid)
            return user[0].name
        except KeyError:
            return False


    def updater(self, cli, event):
        upd = updater.pyCoUpdater(cli, event, self.mconf, self)
        folder = "modules"
        for the_file in os.listdir(folder):
            #file_path = os.path.join(folder, the_file)
            try:
                f = open('modules/%s/%s.json' % (the_file, the_file))
                j = json.load(f)
                upd.addfile(j['type'], the_file, user=j['user'], repo=j['repo'],
                 url=j['url'])
            except IOError:
                pass
        if upd.update() is True:
            self.restart_program("[UPDATE] Aplicando actualizaciones")

    def auth(self, event):
        #session = self.session()
        passw = hashlib.sha1(event.splitd[1].encode('utf-8')).hexdigest()
        u = User.select().where(User.name == event.splitd[0].lower())
        try:
            if u[0].password == passw:
                self.authd[event.source] = u[0].uid
                self.server.privmsg(event.target, "Autenticado exitosamente")
        except:
            self.server.privmsg(event.target, "\00304Error\003: Usuario o " +
            "contraseña incorrectos")

    # Procesa timehandlers (función interna)
    def timehandler(self, hid, tme, c, f):
        while self.timehandlers[hid][0] is True:
            time.sleep(tme)
            getattr(c, f)(self, self.server)

    # Añade un timehandler. Parametros: intervalo en segundos, modulo, funcion
    def addTimeHandler(self, interval, module, func):
        self.timehandlers.append([True, module])
        _thread.start_new_thread(self.timehandler, (len(self.timehandlers) - 1,
            interval, module, func))

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
        h['id'] = self.server.addhandler(numeric, getattr(modulo, func))
        self.handlers.append(h)

        logging.debug("Registrado handler en '%s' ('%s')"
           % (self.conf['server'], numeric))

    def addCommandHandler(self, command, module, chelp="", cpriv=-1,
         cprivchan=False, privmsgonly=False, alias=[]):
        """ Registra un commandHandler con el bot (un comando, bah)
        Parametros:
            - command: Nombre del comando que se va a registrar
            - module: 'self' del módulo donde se registra el handler
            - chelp: La ayuda del comando
            - cpriv: Privilegios requeridos para usar el comando
            - privmsgonly: si el comando solo debe ser ejecutado por privmsg
            - cprivchan: si se aplicarán privilegios por canal.
        Los comandos se accionan al escribir <prefijo>comando;
         <nickdelbot>, comando; <nickdelbot>: comando y <nickdelbot> comando """
        h = {}
        h['mod'] = module
        h['cpriv'] = cpriv
        h['cprivchan'] = cprivchan
        h['privmsgonly'] = privmsgonly
        h['chelp'] = chelp
        h['alias'] = command
        self.commandhandlers[command] = h
        for i, val in enumerate(alias):
            self.commandhandlers[val] = h

        logging.debug("Registrado commandHandler en '%s' ('%s')"
         % (self.conf['server'], command))

    # Retorna true si "module" está cargado
    def is_loaded(self, module):
        try:
            self.modinfo[module]
            return True
        except KeyError:
            return False

    # Retorna un objeto de "module", o si no está cargado, False
    def getmodule(self, module):
        if self.is_loaded(module) is True:
            return self.modules[module]
        else:
            return False

    # carga de modulos
    def loadmod(self, module, cli):
        logging.info('Cargando modulo "%s" en %s'
         % (module, self.conf['server']))
        try:
            self.modinfo[module]
            logging.warning("Se ha intentado cargar un módulo que ya estaba"
             "cargado!!")
            return 3
        except KeyError:
            pass
        try:
            nclassname = "m" + str(int(time.time())) + "x" + module
            shutil.copytree("modules/%s/" % module, "tmp/%s/%s" % (self.conf
             ['pserver'], nclassname))
            touch("tmp/%s/%s/__init__.py" % (self.conf['pserver'], nclassname))
            try:
                self.modules[module] = my_import("tmp." + self.conf['pserver'] +
                "." + nclassname + "." + module + "." + module)(self,
                 self.server)
            except AttributeError as q:
                if str(q) == "'module' object has no attribute '" + module + \
                    "'":
                    logging.error("No se pudo cargar el modulo '%s'. No se ha" %
                     module + " encontrado la clase principal.")
                else:
                    logging.error("No se ha podido cargar el módulo '%s'"
                        " debido a algun error interno en su __init__: %s" % (
                        module, q))
                return 2
            self.modinfo[module] = nclassname
            self.modname[self.modules[module]] = module
        except IOError:
            logging.error("No se pudo cargar el modulo '%s'. No se ha" %
             module + " encontrado el archivo.")
            return 1

    def unloadmod(self, module):
        logging.info('Des-cargando modulo "%s" en %s'
         % (module, self.conf['server']))
        try:
            self.modules[module]
        except KeyError:
            logging.error("El modulo %s no existe o no esta cargado" % module)
            return 1
        shutil.rmtree("tmp/%s/%s" % (self.conf['pserver'], self.modinfo
         [module]))
        del self.modinfo[module]
        # Eliminamos los handlers..
        for i, val in enumerate(self.handlers):
            if self.modules[module] == self.handlers[i]['mod']:
                logging.debug('Eliminando handler "%s" del modulo %s en %s'
                 % (self.handlers[i]['numeric'], module, self.conf['server']))
                self.server.delhandler(self.handlers[i]['id'])
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
        # Matamos a los timehandlers..
        for k, i in enumerate(self.timehandlers):
            if i[1] == self.modules[module]:
                self.timehandlers[k][0] = False

    def restart_program(self, quitmsg):
        for i in enumerate(self.botcli.boservers):
            try:
                i[1].server.quit(quitmsg)
            except:
                pass  # guh..
        python = sys.executable
        os.execl(python, python, * sys.argv)


def my_import(cl):
        d = cl.rfind(".")
        classname = cl[d + 1:len(cl)]
        m = __import__(cl[0:d], globals(), locals(), [classname])
        return getattr(m, classname)


def touch(fname):
    if os.path.exists(fname):
        os.utime(fname, None)
    else:
        open(fname, 'w').close()
