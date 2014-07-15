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
            print("Parámetros:")
            print("    -h --help:          Muestra este texto.")
            print("    -s --stop:          Detiene el demonio.")
            print("    -r --restart:       Reinicia el demonio.")
            print("    -f --foreground     Inicia al bot normalmente (no como "
                                                                "demonio")
            print("       --pid <archivo>  Inicia el bot utilizando otro"
                                                                " pidfile")
            print("    Sin parámetros:     Inicia el demonio")
    except IndexError:
        pyco.start()
