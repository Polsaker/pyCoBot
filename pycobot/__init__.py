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
