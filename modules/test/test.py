import pprint
import irc.client


class test:
    def __init__(self, core, client):
        core.addHandler("welcome", self, "welcomecatch")
        core.addCommandHandler("test", self)
        core.addCommandHandler("test2", self, cpriv=1, cprivchan=True)

    def welcomecatch(self, client, event):
        print("Esto funciona :O")

    def helloworld(self, bot, cli, event):
        cli.msg(event.target, irc.client.parse_nick(event.source)[1] +
         ": Esto es una prueba!")
