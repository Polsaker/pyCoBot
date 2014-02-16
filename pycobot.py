#!/usr/bin/python
# -*- coding: utf-8 -*-

from irc.client import ClientPool
import sys
import json
import logging
import shutil
import os
from pycobot.pycobot import pyCoBot
#from pprint import pprint
# Variables globales:
conf = {}  # Configuración
servers = []  # Servidores
client = None


def main():

    #logging.basicConfig(level=logging.DEBUG)

    try:
        jsonConf = open("pycobot.conf").read()
    except IOError:
        logging.error('No se ha podido abrir el archivo de configuración')
        sys.exit("Missing config file!")

    conf = json.loads(jsonConf)  # Cargar la configuración
    loglevel = conf['config']['loglevel']
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level, filename=conf['config']['logfile'],
     filemode='w')
    # Al iniciar borramos todo lo que hay en tmp/
    folder = 'tmp'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if not file_path == "tmp/__init__.py":
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                else:
                    shutil.rmtree(file_path)
        except Exception:
            pass

    client = ClientPool()

    # Añadir servidores
    for i, val in enumerate(conf['irc']):
        # Para que las carpetas no tengan puntos en sus nombres, asi no
        # confundimos a python... o no?
        conf['irc'][i]['pserver'] = conf['irc'][i]['server'].replace(".", "")
        if not os.path.exists("tmp/" + conf['irc'][i]['pserver']):
            os.makedirs("tmp/" + conf['irc'][i]['pserver'])
            l = open("tmp/" + conf['irc'][i]['pserver'] + "/__init__.py", "w")
            l.write("# :P")  # Con un __init__.py
        servers.append(pyCoBot(conf['irc'][i]['server'], client,
         conf['irc'][i], conf, i))
    client.boservers = servers
    client.process_forever()

if __name__ == "__main__":
    main()
