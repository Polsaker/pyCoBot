class m_modules:
    def __init__(self, core, client):
        core.addCommandHandler("loadmod", self, cpriv=9, chelp="loadmod.help")
        core.addCommandHandler("unloadmod", self, cpriv=9,
            chelp="unloadmod.help")
        core.addCommandHandler("reloadmod", self, cpriv=9,
            chelp="reloadmod.help")

    def reloadmod(self, bot, cli, event):
        self.unloadmod(bot, cli, event)
        self.loadmod(bot, cli, event)

    def loadmod(self, bot, cli, event):
        if not len(event.splitd) > 0:
            cli.msg(event.target, bot._(event, 'core', "generic.missigparam"))
            return 1
        r = bot.loadmod(event.splitd[0], cli)
        if r == 1:
            cli.msg(event.target, bot._(event, self, "err.missigfile"))
        elif r == 2:
            cli.msg(event.target, bot._(event, self, "err.missigclass"))
        elif r == 3:
            cli.msg(event.target, bot._(event, self, "err.alreadyloaded"))
        elif r == 4:
            cli.msg(event.target, bot._(event, self, "err.syntaxerror"))
        else:
            cli.msg(event.target, bot._(event, self, "moduleloaded").format(
                                                            event.splitd[0]))

    def unloadmod(self, bot, cli, event):
        if not len(event.splitd) > 0:
            cli.msg(event.target, bot._(event, 'core', "generic.missigparam"))
            return 1
        if bot.unloadmod(event.splitd[0]) == 1:
            cli.msg(event.target, bot._(event, self, "err.notloaded"))
        else:
            cli.msg(event.target, bot._(event, self, "moduleunloaded").format(
                                                            event.splitd[0]))
