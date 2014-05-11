# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import json


class weather:

    def __init__(self, core, client):
        try:
            self.apikey = core.mconf['moduleconf']['wundergroundapikey']
            if self.apikey == "":
                return None
        except:
            return None

        core.addCommandHandler("tiempo", self, chelp="Muestra el pronóstico" +
        " del tiempo para una ciudad. Sintaxis: tiempo <ciudad>",
        alias=['weather', 'comoestaen'])

    def tiempo(self, bot, cli, event):
        if len(event.splitd) > 0:
            ts = urllib.parse.quote_plus(" ".join(event.splitd)).replace("+",
                "%20")
        else:
            cli.msg(event.target, "\00304Error\003: Faltan parametros")

        r = urllib.request.urlopen("http://api.wunderground.com/api/%s/conditi"
        "ons/forecast/lang:es/q/%s.json" %
         (self.apikey, ts)).read()
        w = json.loads(r.decode('utf-8'))
        try:
            w['current_observation']
        except KeyError:
            resp = "\00304Error\003: No se ha encontrado la ciudad. "
            try:
                w['response']['results']
                resp = resp + "Quizás quiso decir: "
                j = 0
                for val in w['response']['results']:
                    j = j + 1
                    resp = resp + "\2\"%s, %s\"\2 (zmw:%s), " % \
                    (val['city'], val["country_name"], val['zmw'])
                    if j >= 10:
                        continue
            except:
                pass
            cli.msg(event.target, resp)
            return 1
        resp = "El tiempo en \00310\2%s\003\2: Viento a \2%s\2 km/h (\2%s" \
        "\2), " % (w['current_observation']['display_location']['full'],
        w['current_observation']['wind_kph'],
        w['current_observation']['wind_dir'])
        resp = resp + "presión \2%s\2 hPa. Temperatura: \2%s\2ºC, Sensació"\
        "n térmica: \2%s\2ºC [\2%s\2]" % (w['current_observation']['pressu'
        're_mb'], w['current_observation']['temp_c'], w['current_observati'
        'on']['feelslike_c'], self._conv(w['current_observation']['icon']))
        fc = w['forecast']['simpleforecast']['forecastday']
        resp = resp + "Pronóstico: \00303Hoy\003 [\2%s\2], máxima de " \
        "\2%s\2ºC, mínima de \2%s\2ºC, " % (self._conv(fc[0]['icon']),
        fc[0]['high']['celsius'], fc[0]['low']['celsius'])

        resp = resp + "Pronóstico: \00303%s\003 [\2%s\2], máxima de " \
        "\2%s\2ºC, mínima de \2%s\2ºC, " % (self._convday(fc[1]['date']
        ['weekday']), self._conv(fc[1]['icon']), fc[1]['high']['celsius'],
        fc[1]['low']['celsius'])

        resp = resp + "Pronóstico: \00303%s\003 [\2%s\2], máxima de " \
        "\2%s\2ºC, mínima de \2%s\2ºC" % (self._convday(fc[2]['date']
        ['weekday']), self._conv(fc[2]['icon']), fc[2]['high']['celsius'],
        fc[2]['low']['celsius'])

        cli.msg(event.target, resp)

    def _convday(self, c):
        if c == "Monday":
            return "Lunes"
        elif c == "Sunday":
            return "Domingo"
        elif c == "Tuesday":
            return "Martes"
        elif c == "Wednesday":
            return "Miercoles"
        elif c == "Thursday":
            return "Jueves"
        elif c == "Friday":
            return "Viernes"
        elif c == "Saturday":
            return "Sábado"

    def _conv(self, c):
        if c == "clear":
            return "Despejado"
        elif c == "mostlysunny":
            return "Parcialmente despejado"
        elif c == "sunny":
            return "Soleado"
        elif c == "partlycloudy" or c == "mostlycloudy":
            return "Parcialmente nublado"
        elif c == "mist" or c == "foggy" or c == "fog":
            return "Niebla"
        elif c == "chancerain":
            return "Posibles precipitaciones"
        elif c == "rain":
            return "Lluvia"
        elif c == "chancestorms":
            return "Posibles tormentas"
        elif c == "storm":
            return "Tormentas"
        elif c == "snow":
            return "Nevadas"
        elif c == "cloudy":
            return "Nublado"
        elif c == "showers":
            return "Chubascos"
        elif c == "thunderstorm" or c == "tstorms":
            return "Tormentas eléctricas"
        elif c == "icy":
            return "Helado"
        elif c == "chancetstorms":
            return "Posibles tormentas eléctricas"
        elif c == "sleet":
            return "Aguanieve"
