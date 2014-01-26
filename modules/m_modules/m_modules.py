class m_modules:
    def __init__(self, core, client):
        core.addCommandHandler("loadmod", self, "loadmod", cpriv=9, chelp=
        "Carga un módulo. Sintaxis: loadmod <módulo>")
        core.addCommandHandler("unloadmod", self, "unloadmod", cpriv=9, chelp=
        "Descarga un módulo. Sintaxis: unloadmod <módulo>")

    def loadmod(self, bot, cli, event):
        if not len(event.splitd) > 0:
            cli.privmsg(event.target, "\00304Error\003: Faltan parametros")
            return 1
        bot.loadmod(event.splitd[0], cli)
        cli.privmsg(event.target, "Se ha cargado el módulo " + event.splitd[0])

    def unloadmod(self, bot, cli, event):
        if not len(event.splitd) > 0:
            cli.privmsg(event.target, "\00304Error\003: Faltan parametros")
            return 1
        bot.unloadmod(event.splitd[0])
        cli.privmsg(event.target, "Se ha descargado el módulo " +
         event.splitd[0])
