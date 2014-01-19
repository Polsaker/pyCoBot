import pprint
import irc.client
class test:
    def __init__(self, core , client):
        core.addHandler("welcome", self, "welcomecatch")
        core.addCommandHandler("test", self, "helloworld")
    
    def welcomecatch(self, client):
        print("Esto funciona :O")
    
    def helloworld(self, bot, cli, event):
        cli.privmsg(event.target, irc.client.parse_nick(event.source)[1] + ": Esto es una prueba!")
