# -*- coding: utf-8 -*-
from .network import Server
import logging
import time
import gettext
from .database import Settings

logger = logging.getLogger('pyCoBot')


class pyCoBot:
    servers = {}
    config = None
    daemon = None
    donotdie = False

    def __init__(self, daemon):
        logger.info("Starting.")
        self.refreshSettingsCache()
        self.config = daemon.config
        self.daemon = daemon

        for i in self.config.get("servers"):
            logger.debug("Starting server '{0}'.".format(i))
            self.servers[i] = Server(self, i)

    def run(self):
        for i in self.servers:
            self.servers[i].connect()

        # :D
        alive = True
        while alive or self.donotdie:
            time.sleep(1)  # Grooo!
            alive = False
            for i in self.servers:
                if self.servers[i].connection.connected is True or  \
                                     self.servers[i].connection.reconncount <= \
                                          self.servers[i].connection.reconnects:
                    alive = True
    
    def refreshSettingsCache(self):
        self.settingscache = {'global': {}, 'network': {}, 'channel': {}}
        table = Settings.select()
        
        for setting in table:
            if setting.type == "channel":
                try:
                    self.settingscache['channel'][setting.network]
                except:
                    self.settingscache['channel'][setting.network] = {}
                
                try:
                    self.settingscache['channel'][setting.network][setting.channel]
                except:
                    self.settingscache['channel'][setting.network][setting.channel] = {}
                
                self.settingscache['channel'][setting.network][setting.channel][setting.name] = setting.value
            elif setting.type == 'network':
                try:
                    self.settingscache['network'][setting.network]
                except:
                    self.settingscache['network'][setting.network] = {}
                
                self.settingscache['network'][setting.network][setting.name] = setting.value
            elif setting.type == 'global':
                self.settingscache['global'][setting.name] = setting.value
                
                
    def getSettingFromCache(self, stype, name, network=None, channel=None):
        if stype == "channel":
            return self.settingscache['channel'][network][channel][name]
        elif stype == "network":
            return self.settingscache['channel'][network][name]
        elif stype == "global":
            return self.settingscache['channel'][name]
