# -*- coding: utf-8 -*-
from pycobot import Command
from pycobot import Module

class modules(Module):        
    @Command("loadmod", help="Loads a module. Usage: loadmod <module>", privs=10)
    def loadmod(self, bot, cli, ev):
        result = bot.loadModule(ev.splitd[0])
        if result == -1:
            bot.msg(ev.target, _("\00304Error\003: The module does not exist."))
        elif result == -2:
            bot.msg(ev.target, _("\00304Error\003: The module's main file does not exist."))
        elif result == -3:
            bot.msg(ev.target, _("\00304Error\003: The module is already loaded!"))
        elif result == -4:
            bot.msg(ev.target, _("\00304Error\003: Error loading the module (the class doesn't exist or there is a problem on the __init__ function)"))
        else:
            bot.msg(ev.target, _("Module {0} loaded").format(ev.splitd[0]))
    
    @Command("unloadmod", help="Unloads a module. Usage: loadmod <module>", privs=10)
    def unloadmod(self, bot, cli, ev):
        result = bot.unloadModule(ev.splitd[0])
        if result == -1:
            bot.msg(ev.target, _("\00304Error\003: The module is not loaded!"))
        else:
            bot.msg(ev.target, _("Module {0} unloaded").format(ev.splitd[0]))
    
    @Command("reloadmod", help="Unloads and then loads a module. Usage: reloadmod <module>", privs=10)
    def unloadmod(self, bot, cli, ev):
        # ;D
        self.unloadmod(bot, cli, ev)
        self.loadmod(bot, cli, ev)
