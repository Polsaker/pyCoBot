class test:
    def __init__(self, core, client):
        core.addHandler("welcome", self, "welcomecatch")
        core.addCommandHandler("test", self)
        core.addCommandHandler("test2", self, cpriv=1, cprivchan=True)

    def welcomecatch(self, client, event):
        print("Esto funciona :O")

    def test(self, bot, cli, event):
        for k in cli.channels:
            cli.msg(event.target, "Canal: " + k)
            for l in cli.channels[k].users:
                cli.msg(event.target, "  Usuario: " + l + " OP:" +
                        str(cli.channels[k].users[l].is_op) + " VOICE:" +
                        str(cli.channels[k].users[l].is_voiced) + " ACC:" +
                        str(cli.channels[k].users[l].account or ""))
