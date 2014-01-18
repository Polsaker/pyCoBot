class test:
    def __init__(self, chandler, client):
        chandler.addHandler(client.host, "welcome", "test", "welc")
        
    def welc (client, server, *kwargs):
        print("IT RUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUNS!!")
