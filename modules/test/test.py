import pprint
class test:
    def __init__(self, server, core , client):
        core.addHandler(server, "welcome", self, "welcomecatch")
    
    def welcomecatch(self, server, client):
        print("Esto funciona :O")
