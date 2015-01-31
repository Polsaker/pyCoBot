# -*- coding: utf-8 -*-
from pycobot import Command
from pycobot import Module
from socket import timeout
import html.parser as HTMLParser
import urllib.request
import urllib.parse
import re
class wolfram(Module):
    @Command("wa", help="Wolfram Alpha calculator. \00304Usage:\003 wa <question>. \00304Example:\003 wa sun mass / earth mass", alias=['wolfram'])
    def wa(self, bot, cli, ev):
        if not len(ev.splitd) > 0:
            return bot.msg(ev.target, _("\00304Error:\003 I need a search term"))
        query = ' '.join(ev.splitd)
        uri = 'http://tumbolia.appspot.com/wa/' + urllib.parse.quote_plus(query.replace('+', 'plus'))
        try:
            answer = urllib.request.urlopen(uri, timeout=40).read().decode('utf-8')
        except Exception as error:
            return bot.msg(ev.target, _('\00304Error:\003 {0}').format(str(error)))
        if answer:
            answer = HTMLParser.HTMLParser().unescape(answer)
            match = re.search('\\\:([0-9A-Fa-f]{4})', answer)
            if match is not None:
                char_code = match.group(1)
                char = unichr(int(char_code, 16))
                answer = answer.replace('\:' + char_code, char)
            waOutputArray = answer.split(";")
            if(len(waOutputArray) < 2):
                if(answer.strip() == "Couldn't grab results from json stringified precioussss."): #Harcorded, I know it, sorry :(
                # Answer isn't given in an IRC-able format xD, just link to it.
                    bot.msg(ev.target, _("\00304Error:\003 Couldn't display answer, please try http://www.wolframalpha.com/input/?i={0}").format(query.replace(' ', '+')))
                else:
                        bot.msg(ev.target, _('\00304Error:\003 {0}').format(answer))
            else:
                bot.msg(ev.target, "\00304{0}\003 = {1}".format(waOutputArray[0], waOutputArray[1]))
        else:
            bot.msg(ev.target, _("Sorry, I can't get results for that expression."))
