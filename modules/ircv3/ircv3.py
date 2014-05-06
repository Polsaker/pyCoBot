# -*- coding: utf-8 -*-
import base64


class ircv3:

    def __init__(self, core, client):
        self.sasl = True
        try:
            self.conf = core.conf['moduleconf']['nickserv']
            if core.conf['moduleconf']['nickserv']['password'] == "":
                self.sasl = False
        except:
            self.sasl = False
        

        core.addHandler("connect", self, "onconnect")
        core.addHandler("cap", self, "oncap")

    def oncap(self, client, event):
        if event.arguments[0] == "LS":
            if self.sasl is True:
                client.cap('REQ', 'sasl')
                client.send('AUTHENTICATE PLAIN')
                bs = self.conf['user'] + "\0" + self.conf['user'] + "\0" + self.conf['password']
                bs = base64.b64encode(bs.encode('utf-8'))
                client.send('AUTHENTICATE ' + b64.decode('utf-8'))
                client.cap('END')
            
    def onconnect(self, client, event):
        client.cap("LS")
