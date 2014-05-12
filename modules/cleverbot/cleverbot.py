import urllib.request
import hashlib
import re
import html.parser
import time


class cleverbot:
    def __init__(self, core, client):
        core.addCommandHandler("cleverbot", self, chelp="cleverbot.help",
            alias=['cb'])
        self.chans = {}
    
    def cleverbot(self, bot, cli, ev):
        if len(ev.splitd) == 0:
            cli.msg(event.target, bot._(event, 'core', "generic.missigparam"))
            return 1
        try:
            self.chans[ev.target]
            if (time.time() - self.chans[ev.target]['ts']) > 1800:
                del self.chans[ev.target]['bot']
                self.chans[ev.target]['bot'] = Session()
        except:
            self.chans[ev.target] = {}
            self.chans[ev.target]['bot'] = Session()
        self.chans[ev.target]['ts'] = time.time()
        
        cli.msg(ev.target, self.chans[ev.target]['bot'].Ask(s))


class ServerFullError(Exception):
        pass
 
ReplyFlagsRE = re.compile('<INPUT NAME=(.+?) TYPE=(.+?) VALUE="(.*?)">',
                                                 re.IGNORECASE | re.MULTILINE)
 
 
class Session(object):
        keylist = ['stimulus', 'start', 'sessionid', 'vText8', 'vText7',
                'vText6', 'vText5', 'vText4', 'vText3', 'vText2', 'icognoid',
                'icognocheck', 'prevref', 'emotionaloutput', 'emotionalhistory',
                'asbotname', 'ttsvoice', 'typing', 'lineref', 'fno', 'sub',
                'islearning', 'cleanslate']
        headers = {}
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1)"\
                                " Gecko/20100101 Firefox/7.0'
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;" \
                            "q=0.9,*/*;q=0.8'
        headers['Accept-Language'] = 'en-us;q=0.8,en;q=0.5'
        headers['X-Moz'] = 'prefetch'
        headers['Accept-Charset'] = 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
        headers['Referer'] = 'http://www.cleverbot.com'
        headers['Cache-Control'] = 'no-cache, no-cache'
        headers['Pragma'] = 'no-cache'
 
        def __init__(self):
                self.arglist = ['', 'y', '', '', '', '', '', '', '', '', 'wsf',
                    '', '', '', '', '', '', '', '', '0', 'Say', '1', 'false']
                self.MsgList = []
 
        def Send(self):
                data = encode(self.keylist, self.arglist)
                digest_txt = data[9:35].encode('utf-8')
                hash2 = hashlib.md5(digest_txt).hexdigest()
                self.arglist[self.keylist.index('icognocheck')] = hash2
                data = encode(self.keylist, self.arglist)
                binary_data = data.encode('utf-8')
                with urllib.request.urlopen("http://www.cleverbot.com/webservi"
                                            "cemin", binary_data, 5000) as url:
                    reply = url.read()
                return reply
 
        def Ask(self, q):
                self.arglist[self.keylist.index('stimulus')] = q
                if self.MsgList:
                    self.arglist[self.keylist.index('lineref')] = '!0' + \
                                                str(len(self.MsgList) / 2)
                asw = self.Send()
                self.MsgList.append(q)
                answer = parseAnswers(asw)
                for k, v in list(answer.items()):
                        try:
                                self.arglist[self.keylist.index(k)] = v
                        except ValueError:
                                pass
                self.arglist[self.keylist.index('emotionaloutput')] = ''
                text = answer['ttsText']
                self.MsgList.append(text)
                h = html.parser.HTMLParser()
                text = h.unescape(text)
                return text
 
 
def parseAnswers(text):
        d = {}
        keys = ["text", "sessionid", "logurl", "vText8", "vText7", "vText6",
                "vText5", "vText4", "vText3", "vText2", "prevref", "foo",
                "emotionalhistory", "ttsLocMP3", "ttsLocTXT", "ttsLocTXT3",
                "ttsText", "lineRef", "lineURL", "linePOST", "lineChoices",
                        "lineChoicesAbbrev", "typingData", "divert"]
        text = str(text, 'utf-8')
        values = text.split("\r")
        i = 0
        for key in keys:
                d[key] = values[i]
                i += 1
        return d
 
 
def encode(keylist, arglist):
        text = ''
        for i in range(len(keylist)):
                k = keylist[i]
                v = quote(arglist[i])
                text += '&' + k + '=' + v
        text = text[1:]
        return text
 
always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')
 
 
def quote(s, safe='/'):  # quote('abc def') -> 'abc%20def'
        safe += always_safe
        safe_map = {}
        for i in range(256):
                c = chr(i)
                safe_map[c] = (c in safe) and c or ('%%%02X' % i)
        res = list(map(safe_map.__getitem__, s))
        return ''.join(res)
