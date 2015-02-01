# -*- coding: utf-8 -*-
from pycobot import Handler
class nickserv:
    def __init__(self, bot):
        try:
            if bot.getSetting("nickserv.user") == "" or bot.getSetting("nickserv.password") == "":
                bot.logger.warning("No username or password defined for nickserv")
                pass
        except:
            bot.logger.debug("No username or password block defined for nickserv")
            pass
        self.nick = bot.getSetting("nickserv.user")
        self.password = bot.getSetting("nickserv.password")
    @Handler("welcome")
    def identify(self, bot, cli, ev):
        if not self.nick or not self.password:
            return
        bot.logger.info("Trying to identify as {0}".format(self.nick))
        cli.privmsg("NickServ", "IDENTIFY {0} {1}".format(self.nick, self.password))
