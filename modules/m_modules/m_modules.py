class test:
    def __init__(self, core, client):
        core.addCommandHandler("loadmod", self, "loadmod")
        core.addCommandHandler("unloadmod", self, "unloadmod")

    def loadmod(self, bot, cli, event):
        if not len(event.splitd) > 1:
            cli.privmsg(event.target, "\00304Error\003: Faltan parametros")
        bot.loadmod(event.splitd[1], cli)
        cli.privmsg(event.target, "Se ha cargado el módulo " + event.splitd[1])

    def unloadmod(self, bot, cli, event):
        if not len(event.splitd) > 1:
            cli.privmsg(event.target, "\00304Error\003: Faltan parametros")
        bot.unloadmod(event.splitd[1])
        cli.privmsg(event.target, "Se ha descargado el módulo " +
         event.splitd[1])
