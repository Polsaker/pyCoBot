# -*- coding: utf-8 -*-
from pycobot import Handler
from pycobot import Command

class example:
    def __init__(self, bot):
        pass
    
    @Handler("welcome")
    def testcommand(self, bot, cli, ev):
        print("PO TA TO ES")
        print(_("WOOOOOOOOOOOOO IT WOORKS"))
    
    @Command("test", help="Comando de ejemplo")
    def testcmd(self, bot, cli, ev):
        bot.msg(ev.target, "Hola mundo")
