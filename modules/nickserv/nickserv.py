# -*- coding: utf-8 -*-


class nickserv:

    def __init__(self, core, client):
        try:
            if core.conf['moduleconf']['nickserv']['password'] == "":
                return None
        except:
            return None
        self.conf = core.conf['moduleconf']['nickserv']

        core.addHandler("welcome", self, "identify")

    def identify(self, client):
        client.privmsg("NickServ", "IDENTIFY " + self.conf['user'] + " " +
         self.conf['password'])