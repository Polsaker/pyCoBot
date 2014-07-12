#!/usr/bin/python3
# -*- coding: utf-8 -*-

from irc.client import ClientPool
import sys
import logging
from pycobot.pycobot import pyCoBot
from pycobot.kaptan import Kaptan
#from pprint import pprint
# Variables globales:
conf = {}  # Configuración
servers = []  # Servidores
client = None

import os
import time
import atexit
from signal import SIGTERM


class Daemon:
        client = None  # ;D

        def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null',
                     stderr='/dev/null'):
                self.stdin = stdin
                self.stdout = stdout
                self.stderr = stderr
                self.pidfile = pidfile

        def daemonize(self):
                """
                do the UNIX double-fork magic, see Stevens' "Advanced
                Programming in the UNIX Environment" for details
                            (ISBN 0201563177)
                http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
                """
                try:
                        pid = os.fork()
                        if pid > 0:
                                # exit first parent
                                sys.exit(0)
                except OSError as e:
                        sys.stderr.write("fork #1 failed: %d (%s)\n" %
                                                    (e.errno, e.strerror))
                        sys.exit(1)

                # decouple from parent environment
                #os.chdir("/")
                os.setsid()
                os.umask(0)

                # do second fork
                try:
                        pid = os.fork()
                        if pid > 0:
                                # exit from second parent
                                sys.exit(0)
                except OSError as e:
                        sys.stderr.write("fork #2 failed: %d (%s)\n" %
                                                 (e.errno, e.strerror))
                        sys.exit(1)

                # redirect standard file descriptors
                sys.stdout.flush()
                sys.stderr.flush()
                si = open(self.stdin, 'r')
                so = open(self.stdout, 'a+')
                se = open(self.stderr, 'a+')
                os.dup2(si.fileno(), sys.stdin.fileno())
                os.dup2(so.fileno(), sys.stdout.fileno())
                os.dup2(se.fileno(), sys.stderr.fileno())

                # write pidfile
                atexit.register(self.delpid)
                pid = str(os.getpid())
                open(self.pidfile, 'w+').write("%s\n" % pid)

        def delpid(self):
                os.remove(self.pidfile)

        def start(self):
                """
                Start the daemon
                """
                # Check for a pidfile to see if the daemon already runs
                try:
                        pf = open(self.pidfile, 'r')
                        pid = int(pf.read().strip())
                        pf.close()
                except IOError:
                        pid = None

                if pid:
                        message = "pidfile %s already exist. Daemon" \
                                    " already running?\n"
                        sys.stderr.write(message % self.pidfile)
                        sys.exit(1)

                # Start the daemon
                self.daemonize()
                self.run()

        def stop(self):
                """
                Stop the daemon
                """
                # Get the pid from the pidfile
                try:
                        pf = open(self.pidfile, 'r')
                        pid = int(pf.read().strip())
                        pf.close()
                except IOError:
                        pid = None

                if not pid:
                        message = "pidfile %s does not exist. Daemon not" \
                                " running?\n"
                        sys.stderr.write(message % self.pidfile)
                        return  # not an error in a restart

                # Try killing the daemon process
                try:
                        while 1:
                                os.kill(pid, SIGTERM)
                                time.sleep(0.1)
                except OSError as err:
                        err = str(err)
                        if err.find("No such process") > 0:
                                if os.path.exists(self.pidfile):
                                        os.remove(self.pidfile)
                        else:
                                print((str(err)))
                                sys.exit(1)

        def restart(self):
                """
                Restart the daemon
                """
                self.stop()
                self.start()

        def run(self):
            try:
                jsonConf = open("pycobot.conf").read()
            except IOError:
                logging.error('No se ha podido abrir el archivo de'
                              ' configuración')
                sys.exit("Missing config file!")

            #conf = json.loads(jsonConf)  # Cargar la configuración
            conf = Kaptan(handler="json")
            conf.import_config(jsonConf)
            #loglevel = conf['config']['loglevel']
            loglevel = conf.get("config.loglevel")

            numeric_level = getattr(logging, loglevel.upper(), None)
            if not isinstance(numeric_level, int):
                raise ValueError('Invalid log level: %s' % loglevel)
            logging.basicConfig(level=numeric_level,
                filename=conf.get("config.logfile", sys.stdout), filemode='w')

            self.client = ClientPool()

            # Añadir servidores
            for i, val in enumerate(conf.get("irc")):
                servers.append(pyCoBot(conf.get("irc.{0}.server".format(val)),
                 self.client, conf.get("irc.{0}".format(val)), conf, val, self))
            self.client.boservers = servers
            self.client.process_forever()


def main():
    l = Daemon("/tmp/pycobot.pid",
         stdout="pycobot.log", stderr="pycobot.err")
    try:
        sys.argv[1]
    except:
        l.start()
        return
    if sys.argv[1] == "--stop":
        l.stop()
    elif sys.argv[1] == "--foreground":
        l.run()
    elif sys.argv[1] == "--help":
        print("Uso: pycobot.py [argumentos]:")
        print("\nArgumentos:")
        print("    --help: Muestra este mensaje")
        print("    --stop: Detiene el demonio")
        print("    --foreground: Inicia el bot normalmente (no como demonio)")
        print("    --restart: Reinicia el bot")
        print("\nSin argumentos: Inicia al bot como demonio")
    elif sys.argv[1] == "--restart":
        l.restart()
    else:
        l.start()


if __name__ == "__main__":
    main()
