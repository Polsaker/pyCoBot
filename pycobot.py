#!/usr/bin/python
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


def main():
    try:
        jsonConf = open("pycobot.conf").read()
    except IOError:
        logging.error('No se ha podido abrir el archivo de configuración')
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
        filename=conf.get("config.logfile"), filemode='w')

    client = ClientPool()

    # Añadir servidores
    for i, val in enumerate(conf.get("irc")):
        #conf['irc'][i]['pserver'] = conf['irc'][i]['server'].replace(".", "")
        servers.append(pyCoBot(conf.get("irc.{0}.server".format(val)), client,
         conf.get("irc.{0}".format(val)), conf, val))
    client.boservers = servers
    client.process_forever()

if __name__ == "__main__":
    main()
