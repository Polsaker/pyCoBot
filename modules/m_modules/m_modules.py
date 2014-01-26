class m_modules:
    def __init__(self, core, client):
        core.addCommandHandler("loadmod", self, cpriv=9, chelp=
        "Carga un módulo. Sintaxis: loadmod <módulo>")
        core.addCommandHandler("unloadmod", self, cpriv=9, chelp=
        "Descarga un módulo. Sintaxis: unloadmod <módulo>")

    def loadmod(self, bot, cli, event):
        if not len(event.splitd) > 0:
            cli.privmsg(event.target, "\00304Error\003: Faltan parametros")
            return 1
        r = bot.loadmod(event.splitd[0], cli)
        if r == 1:
            cli.privmsg(event.target, "\00304Error\003: No se ha encontrado e" +
            "l archivo.")
        elif r == 2:
            cli.privmsg(event.target, "\00304Error\003: No se ha encontrado l" +
            "a clase principal.")
        else:
            cli.privmsg(event.target, "Se ha cargado el módulo " + event
             .splitd[0])

    def unloadmod(self, bot, cli, event):
        if not len(event.splitd) > 0:
            cli.privmsg(event.target, "\00304Error\003: Faltan parametros")
            return 1
        if bot.unloadmod(event.splitd[0]) == 1:
            cli.privmsg(event.target, "\00304Error\003: El módulo no está car" +
             "gado")
        else:
            cli.privmsg(event.target, "Se ha descargado el módulo " +
             event.splitd[0])
