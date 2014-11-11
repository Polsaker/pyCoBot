# -*- coding: utf-8 -*-
from pycobot import CommandHandler

class example:
    def __init__(self, bot):
        pass
    
    @CommandHandler(command="test")
    def testcommand(self, bot, cli, ev):
        pass
