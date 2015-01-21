# -*- coding: utf-8 -*-

from .daemon import Daemon
import sys
from .kaptan import Kaptan
from .pycobot import pyCoBot
import logging
from .peewee import peewee
from . import database
import os
import json
import hashlib

VERSION = "2.1"
CODENAME = "Dors"


class bot(Daemon):
    config = None
    pycobot = None
    langs = None
    def __init__(self, pid="/var/tmp/pycobot.pid"):
        super(bot, self).__init__(pid, stdout="pycobot.log",
                                       stderr="pycobot.err")
        try:
            database.obj.create_tables([database.Settings, database.User, database.UserPriv])
            # Annoy the user asking for first user settings.
            print("This looks like the first time you run pyCoBot (or the database got deleted or corrupted)")
            print("Please insert a user/password for the administrative account")
            
            user = input("Username: ").lower()
            passw = input("Password: ")
            
            e = database.User.create(username=user, password=hashlib.sha256(passw.encode()).hexdigest())
            e.save()
            e = database.UserPriv.create(uid=1, priv=10, module="*", channel="*") # First user... id 1, no?
            e.save()
            print("OK")
        except peewee.OperationalError:
            pass  # Tables already created, all OK

        try:
            jsonConf = open("pycobot.conf").read()
        except IOError:
            logging.critical('Couldn\'t open configuration file')
            sys.exit("Missing config file!")
        self.config = Kaptan(handler="json")
        self.config.import_config(jsonConf)

        loglevel = self.config.get("general.logging", "warning")
        numeric_level = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            logging.warning("Invalid log level: {0}".format(loglevel))
        logging.getLogger(None).setLevel(numeric_level)

        if self.config.get("general.loggingsimple", False) is False:
            logging.basicConfig(format="%(asctime)s: %(name)s: %(levelname)"
                    "s (at %(filename)s:%(funcName)s:%(lineno)d): %(message)s")
        else:
            logging.basicConfig()  # :D
        
        langstuff = {}
        
        # Get all the i18n stuff
        # For the core translations..
        for subdir, dirs, files in os.walk("pycobot/lang"):
            for file in files:
                langcode = file.split(".")[0]
                try:
                    langstuff[langcode]
                except:
                    langstuff[langcode] = {}
                l = json.load(open(os.path.join(subdir, file), 'r'))
                for q in l:
                    langstuff[langcode][q] = l[q]
                

        for subdir, dirs, files in os.walk("modules"):
            if "/lang" in subdir:
                for subdir, dirs, files in os.walk(subdir):
                    for file in files:
                        langcode = file.split(".")[0]
                        try:
                            langstuff[langcode]
                        except:
                            langstuff[langcode] = {}
                        l = json.load(open(os.path.join(subdir, file), 'r'))
                        for q in l:
                            langstuff[langcode][q] = l[q]
                            
        self.langs = langstuff
        self.pycobot = pyCoBot(self)

    def run(self):
        self.pycobot.run()

def Handler(*args, **kwargs):
    def call_fn(fn):
        try:
            fn.iamahandler = kwargs['event']
        except:
            fn.iamahandler = args[0]
        return fn
    return call_fn

def CommandHandler(*args, **kwargs):
    def call_fn(fn):
        try:
            fn.iamachandler = kwargs['command']
        except:
            fn.iamachandler = args[0]
        try:
            fn.chelp = kwargs['help']
        except:
            fn.chelp = ''
        try:
            fn.cprivs = kwargs['privs']
        except:
            fn.cprivs = ''
        try:
            fn.calias = kwargs['alias']
        except:
            fn.calias = []
        try:
            fn.cprivfunc = kwargs['privfunc']
        except:
            fn.cprivfunc = None
        fn.module = fn.__init__.__self__.__class__.__name__
        return fn
    return call_fn

Command = CommandHandler

class Module(object):
    def __init__(self, bot):
        pass
