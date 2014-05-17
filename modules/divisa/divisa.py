import time
import json
import urllib.request


class divisa:
    def __init__(self, core, client):
        core.addCommandHandler("conv", self, chelp="conv.help")
        self.thing = None
        self.thingtime = 0
        r = urllib.request.urlopen("http://openexchangerate"
         "s.org/api/latest.json?app_id=" +
         core.readConf("config.openexchratesapikey")).read().decode()
        self.thing = json.loads(r)
        self.thingtime = time.time()
    
    def conv(self, bot, cli, ev):
        if len(ev.splitd) < 2:
            cli.msg(ev.target, bot._(ev, 'core', "generic.missigparam"))
            return 1
        dfrom = ev.splitd[0].upper()
        dto = ev.splitd[1].upper()
        try:
            kfrom = self.thing['rates'][dfrom]
        except:
            cli.msg(ev.target, bot._(ev, self, 'err.invaliddiv').format(dfrom))
            return 1
        try:
            kto = self.thing['rates'][dto]
        except:
            cli.msg(ev.target, bot._(ev, self, 'err.invaliddiv').format(dto))
            return 1
        dfrom = bot._(ev, self, dfrom)
        dto = bot._(ev, self, dto)
            
        if (time.time() - self.thingtime) < 1800:
            r = urllib.request.urlopen("http://openexchangerate"
             "s.org/api/latest.json?app_id=" +
             bot.readConf("config.openexchratesapikey")).read().decode()
            self.thing = json.loads(r)
            self.thingtime = time.time()
        cli.msg(ev.target, bot._(ev, self, 'convmsg').format(dfrom, dto, (kfrom / kto) * float(ev.splitd[2])))
        
