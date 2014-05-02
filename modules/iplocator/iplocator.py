# -*- coding: utf-8 -*-
import .geoip2.database
import os
import logging


class nickserv:

    def __init__(self, core, client):
        if not os.path.exists("modules/iplocator/GeoLite2-City.mmdb"):
            logging.error("No se ha encontrado modules/iplocator/GeoLite2-City.mmdb. Descarguelo y descomprimalo: http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz")
            return 0
        core.addCommandHandler("ip", self, chelp=
        "Geolocaliza una ip. Sintaxis: ip <ip>")
        self.reader = geoip2.database.Reader('modules/iplocator/GeoLite2-City.mmdb')

    def ip(self, bot, cli, event):
        response = self.reader.city('128.101.101.101')
        cli.notice(ev.source, response.city.name)
