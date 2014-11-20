# -*- coding: utf-8 -*-

from .daemon import Daemon
import sys
from .kaptan import Kaptan
from .pycobot import pyCoBot
import logging
from .peewee import peewee

VERSION = "2.1"
CODENAME = "Dors"

database = peewee.SqliteDatabase('db/cobot.db', threadlocals=True)

class bot(Daemon):
    config = None
    pycobot = None

    def __init__(self, pid="/var/tmp/pycobot.pid"):
        super(bot, self).__init__(pid, stdout="pycobot.log",
                                       stderr="pycobot.err")
        database.create_tables([Settings, User, UserPriv], safe=True)

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

    def run(self):
        pycobot = pyCoBot(self)
        pycobot.run()

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
        fn.module = fn.__init__.__self__.__class__.__name__
        return fn
    return call_fn

Command = CommandHandler

class BaseModel(peewee.Model):
    class Meta:
        database = database

class User(BaseModel):
    username = peewee.CharField(unique=True)
    password = peewee.CharField()

class UserPriv(BaseModel):
    uid = peewee.IntegerField()
    priv = peewee.IntegerField()
    module = peewee.CharField()
    channel = peewee.CharField()
    
class Settings(BaseModel):
    type = peewee.CharField()  # Global/Network/Channel
    channel = peewee.CharField()  # Only if it is a channel setting
    network = peewee.CharField()  # Only if it is not a global setting
    name = peewee.CharField()
    value = peewee.CharField()
    
