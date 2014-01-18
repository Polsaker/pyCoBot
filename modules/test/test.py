from oyoyo import helpers
from oyoyo import parse
import pprint

class test:
    def __init__(self, chandler, client):
        chandler.addHandler(client.host, "welcome", self, "welc")
        chandler.addCommandHandler(client.host, "test", self, "testcommand")
        
    def welc (client, server, *kwargs):
        print("Funciona!")
    
    def testcommand(self, client, server, nick, channel, msg):
        helpers.msg(client, channel, ( parse.parse_nick(nick)[1] ) + ": Esto es una prueba!")
