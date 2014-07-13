#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pycobot import daemon
import sys
from pycobot.kaptan import Kaptan
import logging

VERSION = "2.1"
CODENAME = "Dors"

# :D
logging.basicConfig(format="%(asctime)s: %(name)s: %(levelname)s (at %(filename"
                    ")s:%(funcName)s:%(lineno)d): %(message)s")


class bot(daemon.Daemon):
    config = None

    def __init__(self, pid="/var/tmp/pycobot.pid"):
        super(bot, self).__init__(pid, stdout="pycobot.log",
                                       stderr="pycobot.err")

        try:
            jsonConf = open("pycobot.conf").read()
        except IOError:
            logging.critical('No se ha podido abrir el archivo de'
                          ' configuración')
            sys.exit("Missing config file!")
        config = Kaptan(handler="json")
        config.import_config(jsonConf)

    def run(self):
        pass

if __name__ == "__main__":
    pyco = bot()
    try:
        arg = sys.argv[1]
        if arg == "--stop" or arg == "-s":
            pyco.stop()
        elif arg == "--restart" or arg == "-r":
            pyco.restart()
        elif arg == "--foreground" or arg == "-f":
            pyco.run()
        elif arg == "--pid":
            pyco = bot(sys.argv[2])
            pyco.start()
        elif arg == "--help" or arg == "-h":
            print(("pyCoBot v{0} ({1})\n".format(VERSION, CODENAME)))
            print("Parámetros:")
            print("    -h --help:          Muestra este texto.")
            print("    -s --stop:          Detiene el demonio.")
            print("    -r --restart:       Reinicia el demonio.")
            print("    -f --foreground     Inicia al bot normalmente (no como "
                                                                "demonio")
            print("       --pid <archivo>  Inicia el bot utilizando otro"
                                                                " pidfile")
            print("    Sin parámetros:     Inicia el demonio")
    except IndexError:
        pyco.start()
