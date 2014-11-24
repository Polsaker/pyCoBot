#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pycobot
import sys

if __name__ == "__main__":
    pyco = pycobot.bot()
    try:
        arg = sys.argv[1]
        if arg == "--stop" or arg == "-s":
            pyco.stop()
        elif arg == "--restart" or arg == "-r":
            pyco.restart()
        elif arg == "--foreground" or arg == "-f":
            pyco.run()
        elif arg == "--pid":
            pyco = pycobot.bot(sys.argv[2])
            pyco.start()
        elif arg == "--help" or arg == "-h":
            print(("pyCoBot v{0} ({1})\n".format(pycobot.VERSION,
                                                 pycobot.CODENAME)))
            print("Parameters:")
            print("    -h --help:          Shows this help.")
            print("    -s --stop:          Stops the daemon.")
            print("    -r --restart:       Restarts the daemon.")
            print("    -f --foreground     Prevents the bot from forking in the background")
            print("       --pid <archivo>  Start the bot with other pidfile")
            print("    Without parameters: Starts the daemon.")
    except IndexError:
        pyco.start()
