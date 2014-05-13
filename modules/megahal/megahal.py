from time import time
import re


class megahal:
    def __init__(self, core, client):
        self.core = core
        self.brain = MegaHAL2()
        core.addHandler("pubmsg", self, "msghandler")
        core.addHandler("privmsg", self, "msghandler")
        core.addCommandHandler("megahal", self, chelp="hal.help",
            alias=['h', 'hal'])

    def megahal(self, bot, cli, ev):
        if len(ev.splitd) == 0:
            cli.msg(ev.target, bot._(ev, 'core', "generic.missigparam"))
            return 1
        cli.msg(ev.target, self.brain.get_reply(" ".join(ev.splitd)))

    def msghandler(self, cli, ev):
        if self.core._iscommand(ev) is None:
            p2 = re.compile("^" + re.escape(cli.nickname) +
            "[:, ]? (\S{1,52})[ ]?(.*)", re.IGNORECASE)
            m2 = p2.search(ev.arguments[0])
            if m2 is None:
                self.brain.__brain.communicate(ev.arguments[0], reply=False)


# Copyright (c) 2010, Chris Jones
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Python implementation of megahal markov bot"""

import shelve
import random
import math
import os

__version__ = '0.2'
__author__ = 'Chris Jones <cjones@gruntle.org>'
__license__ = 'BSD'
__all__ = ['MegaHAL2', 'Dictionary', 'Tree', '__version__', 'DEFAULT_ORDER',
            'DEFAULT_BRAINFILE', 'DEFAULT_TIMEOUT', "megahal"]

DEFAULT_ORDER = 5
DEFAULT_BRAINFILE = os.path.join(os.environ.get('HOME', ''), '.pymegahal-brain')
DEFAULT_TIMEOUT = 1.0

API_VERSION = '1.0'
END_WORD = '<FIN>'
ERROR_WORD = '<ERROR>'

DEFAULT_BANWORDS = ["A", "HABILIDAD", "CAPAZ", "SOBRE", "ABSOLUTO",
    "ABSOLUTAMENTE", "ATRAVÉS", "ACTUAL", "ENREALIDAD", "DESPUÉS",
    "AGAIN", "ENCONTRA", "AGO", "DEACUERDO", "ALL", "CASI", "ALOLARGO",
    "YA", "AUNQUE", "SIEMPRE", "DE"
    "UN", "Y", "OTRO", "ANY", "TODAS", "NADA", "FORMAS", "SON", "ESTÁN",
    "CERCA", "COMO",
    "TOTAL", "VUELTA", "MALO", "SER", "ESTADO", "ANTES", "ATRÁS", "SER",
    "CREER", "PERTENECER", "MEJOR",
    "ENTRE", "BIG", "MÁS", "GRANDE", "BIT", "AMBAS", "AMIGO", "PERO", "POR",
    "LLAMADA", "LLAMA",
    "CAME", "PUEDE", "NOPUEDO", "NOPUEDO", "CUIDADO", "CUIDADO", "CASE",
    "CATCH", "ATRAPADOS", "CIERTO",
    "CAMBIO", "CLOSE", "CLOSER", "COME", "VENIR", "LASCOMÚN", "CONSTANTE",
    "CONSTANTE", "PODRÍA",
    "DIA", "DAYS", "DERIVADOS", "DESCRIBIR", "DESCRIBE", "DETERMINAR",
    "DETERMINA", "DID", "NO",
    "DOES", "NO", "HACER", "NO", "DUDA", "PALABRA", "DONE", "ABAJO", "CADA",
    "ANTERIOR", "TEMPRANA", "ELSE",
    "ESPECIALMENTE", "INCLUSO", "NUNCA", "TODOS", "TODOS", "TODOELMUNDO",
    "TODO", "HECHO", "JUSTO",
    "FAR", "COMPAÑEROS", "POCOS", "BUSCAR", "BIEN", "A", "FORM", "OTROS", "DE",
    "COMPLETO", "MÁS", "DIO",
    "CONSEGUIR", "DAR", "DADO", "DAR", "GO", "GOING", "GONE", "BUENO", "GOT",
    "CONSEGUIDO", "GRANDE",
    "HA", "NOTIENE", "TENER", "TENER", "CELEBRADA", "AQUÍ", "USAR",
    "ALTO", "EXPLOTACIÓN", "CÓMO",
    "IN", "HE", "INSIDE", "ENLUGAR", "EN", "ES", "NOES", "ESO", "ES", "SU",
    "SOLO", "MANTENER",
    "SABÍA", "SABER", "CONOCIDO", "GRANDE", "MÁSGRANDE", "LARGETS", "LAST",
    "LATE", "DESPUÉS", "MENOS", "MENOS",
    "VAMOS", "NIVEL", "GUSTOS", "LARGO", "YA", "MIRA", "PEQUEÑO", "BUSCADO",
    "MIRAR", "ESPERA", "BAJO",
    "MARCA", "HACIENDO", "MUCHOS", "MATE", "MAYO", "MAYBE", "MEAN", "CONOCER",
    "MENCIÓN", "MERO", "PODRÍA",
    "MAS", "MORNING", "MAS", "MOVER", "MUCHO", "DEBER", "CERCA", "MÁSCERCA",
    "NUNCA", "SIGUIENTE", "AGRADABLE",
    "NINGUNO", "MEDIODÍA", "NADIE", "NO", "NOTA", "NADA", "AHORA", "EVIDENTE",
    "DE", "OFF", "ON", "UNAVEZ",
    "SOBRE", "COMENTARIOS", "O", "OTROS", "NUESTRO", "OUT", "OVER", "PARTE",
    "PROPIO", "PARTICULAR",
    "TALVEZ", "PERSONA", "PIEZA", "LUGAR", "AGRADABLE", "PORFAVOR", "POPULAR",
    "PREFIEREN", "LINDO", "PONER",
    "REAL", "REALMENTE", "RECIBIR", "RECIBIDO", "RECIENTES", "RECIENTEMENTE",
    "RELACIONADOS", "RESULTADO", "RESULTANDO",
    "DIJO", "SAW""MISMO", "DECIR", "DECIR", "VER", "PARECE", "PARECÍA",
    "PARECE", "VE", "RARAVEZ",
    "SET", "VARIOS", "DEBERÁ", "CORTO", "CORTO", "DEBERÍA", "SHOW", "MUESTRA",
    "SIMPLE", "SIMPLEMENTE",
    "SO", "ALGUNOS", "ALGUIEN", "ALGO", "ALGUNAVEZ", "AVECES", "SOMEWHERE",
    "ORDENAR", "CLASES",
    "GASTADO", "TODAVÍA", "COSAS", "TAL", "SUGIEREN", "SUGERENCIA", "SUPONGO",
    "CLARO", "SEGURAMENTE",
    "RODEA", "TOMAR", "TOMADO", "TOMAR", "TELL", "QUE", "GRACIAS", "GRACIAS",
    "QUE", "ESOES",
    "LA", "SU", "ELLOS", "YLUEGO", "NO", "PORLOTANTO", "ESTOS", "ELLOS", "COSA",
    "COSAS", "ESTE",
    "AUNQUE", "PENSAMIENTOS", "THOUROUGHLY", "A", "TINY", "A", "HOY",
    "TOGETHER", "DIJE",
    "DEMASIADO", "TOTAL", "TOTALMENTE", "TOUCH", "TRY", "DOSVECES", "BAJO",
    "ENTENDER", "COMPRENDIDO", "HASTA",
    "EE.UU.", "USADO", "USO", "GENERALMENTE", "VARIOS", "MUY", "BUSCAR",
    "BUSCADO", "QUIERE", "ERA", "RELOJ",
    "CAMINOS", "WE", "ESTAMOS", "BIEN", "FUE", "ERAN", "QUÉ", "CUÁLES",
    "LO", "QUÉ ESTÁ", "CUÁNDO",
    "DÓNDE", "QUE", "MIENTRAS", "MIENTRAS", "OMS", "QUIÉNES", "QUIÉN",
    "VOLUNTAD", "DESEO", "CON", "DENTRO",
    "MARAVILLOSO", "PEOR", "PEOR", "SERÍA", "MAL", "AYER", "AÚN"]
DEFAULT_AUXWORDS = ['EL', 'ELLA', 'SU', 'EL', 'YO', "VOY", "SOY", "FUI",
                     'GUSTA', 'ME',
                    'MI', 'MISMO', 'UNO', 'TRES', 'DOS', 'TU', 'TUS']

DEFAULT_SWAPWORDS = {'ODIO': 'AMOR', 'TU': 'MI', 'NO': 'SI',
                     'TU': 'YO', 'AMOR': 'ODIO', 'MIS': 'TUS',
                     'NO': 'SI'}


class Tree(object):

    def __init__(self, symbol=0):
        self.symbol = symbol
        self.usage = 0
        self.count = 0
        self.children = []

    def add_symbol(self, symbol):
        node = self.get_child(symbol)
        node.count += 1
        self.usage += 1
        return node

    def get_child(self, symbol, add=True):
        for child in self.children:
            if child.symbol == symbol:
                break
        else:
            if add:
                child = Tree(symbol)
                self.children.append(child)
            else:
                child = None
        return child


class Dictionary(list):

    def add_word(self, word):
        try:
            return self.index(word)
        except ValueError:
            self.append(word)
            return len(self) - 1

    def find_word(self, word):
        try:
            return self.index(word)
        except ValueError:
            return 0


class Brain(object):

    def __init__(self, order, filel, timeout):
        self.timeout = timeout
        self.db = shelve.open(filel, writeback=True)
        if self.db.setdefault('api', API_VERSION) != API_VERSION:
            raise ValueError('This brain has an incompatible api version: %d'
                                    ' != %d' % (self.db['api'], API_VERSION))
        if self.db.setdefault('order', order) != order:
            raise ValueError('This brain already has an order of %d'
                             % self.db['order'])
        try:
            self.forward = self.db.setdefault('forward', Tree())
        except:
            self.forward = Tree()
        try:
            self.backward = self.db.setdefault('backward', Tree())
        except:
            self.backward = Tree()
        try:
            self.dictionary = self.db.setdefault('dictionary', Dictionary())
        except:
            self.dictionary = Dictionary()

        self.error_symbol = self.dictionary.add_word(ERROR_WORD)
        self.end_symbol = self.dictionary.add_word(END_WORD)
        try:
            self.banwords = self.bd['banwords']
        except:
            self.banwords = Dictionary(DEFAULT_BANWORDS)
        try:
            self.auxwords = self.db['auxwords']
        except:
            self.auxwords = Dictionary(DEFAULT_AUXWORDS)
        try:
            self.swapwords = self.db.setdefault('swapwords', DEFAULT_SWAPWORDS)
        except:
            self.swapwords = DEFAULT_SWAPWORDS
        self.closed = False

    @property
    def order(self):
        return self.db['order']

    @staticmethod
    def get_words_from_phrase(phrase):
        phrase = phrase.upper()
        words = []
        if phrase:
            offset = 0

            def boundary(string, position):
                if position == 0:
                    boundary = False
                elif position == len(string):
                    boundary = True
                elif (string[position] == "'" and
                    string[position - 1].isalpha() and
                    string[position + 1].isalpha()):
                    boundary = False
                elif (position > 1 and
                    string[position - 1] == "'" and
                    string[position - 2].isalpha() and
                    string[position].isalpha()):
                    boundary = False
                elif (string[position].isalpha() and
                    not string[position - 1].isalpha()):
                    boundary = True
                elif (not string[position].isalpha() and
                    string[position - 1].isalpha()):
                    boundary = True
                elif string[position].isdigit() != \
                    string[position - 1].isdigit():
                    boundary = True
                else:
                    boundary = False
                return boundary

            while True:
                if boundary(phrase, offset):
                    word, phrase = phrase[:offset], phrase[offset:]
                    words.append(word)
                    if not phrase:
                        break
                    offset = 0
                else:
                    offset += 1
            if words[-1][0].isalnum():
                words.append('.')
            elif words[-1][-1] not in '!.?':
                words[-1] = '.'
        return words

    def communicate(self, phrase, learn=True, reply=True):
        words = self.get_words_from_phrase(phrase)
        if learn:
            self.learn(words)
        if reply:
            return self.get_reply(words)

    def get_context(self, tree):

        class Context(dict):

            def __enter__(context):
                context.used_key = False
                context[0] = tree
                return context

            def __exit__(context, *exc_info):
                context.update(self.end_symbol)

            @property
            def root(context):
                return context[0]

            def update(context, symbol):
                for i in range(self.order + 1, 0, -1):
                    node = context.get(i - 1)
                    if node is not None:
                        context[i] = node.add_symbol(symbol)

            def seed(context, keys):
                if keys:
                    i = random.randrange(len(keys))
                    for key in keys[i:] + keys[:i]:
                        if key not in self.auxwords:
                            try:
                                return self.dictionary.index(key)
                            except ValueError:
                                pass
                if context.root.children:
                    return random.choice(context.root.children).symbol
                return 0

            def babble(context, keys, replies):
                for i in range(self.order + 1):
                    if context.get(i) is not None:
                        node = context[i]
                if not node.children:
                    return 0
                i = random.randrange(len(node.children))
                count = random.randrange(node.usage)
                symbol = 0
                while count >= 0:
                    symbol = node.children[i].symbol
                    word = self.dictionary[symbol]
                    if word in keys and (context.used_key or word not in
                                                         self.auxwords):
                        context.used_key = True
                        break
                    count -= node.children[i].count
                    if i >= len(node.children) - 1:
                        i = 0
                    else:
                        i = i + 1
                return symbol

        return Context()

    def learn(self, words):
        if len(words) > self.order:
            with self.get_context(self.forward) as context:
                for word in words:
                    context.update(self.dictionary.add_word(word))
            with self.get_context(self.backward) as context:
                for word in reversed(words):
                    context.update(self.dictionary.index(word))

    def get_reply(self, words):
        keywords = self.make_keywords(words)
        dummy_reply = self.generate_replywords()
        if not dummy_reply or words == dummy_reply:
            output = self.get_words_from_phrase("I don't know enough to"
                                                    " answer yet!")
        else:
            output = dummy_reply

        max_surprise = -1.0
        basetime = time()
        while time() - basetime < self.timeout:
            reply = self.generate_replywords(keywords)
            surprise = self.evaluate_reply(keywords, reply)
            if reply and surprise > max_surprise and reply != keywords:
                max_surprise = surprise
                output = reply

        return ''.join(output).capitalize()

    def evaluate_reply(self, keys, words):
        state = {'num': 0, 'entropy': 0.0}
        if words:

            def evaluate(node, words):
                with self.get_context(node) as context:
                    for word in words:
                        symbol = self.dictionary.index(word)
                        context.update(symbol)
                        if word in keys:
                            prob = 0.0
                            count = 0
                            state['num'] += 1
                            for j in range(self.order):
                                node = context.get(j)
                                if node is not None:
                                    child = node.get_child(symbol, add=False)
                                    if child:
                                        prob += float(child.count) / node.usage
                                    count += 1
                            if count:
                                state['entropy'] -= math.log(prob / count)

            evaluate(self.forward, words)
            evaluate(self.backward, reversed(words))

            if state['num'] >= 8:
                state['entropy'] /= math.sqrt(state['num'] - 1)
            if state['num'] >= 16:
                state['entropy'] /= state['num']
        return state['entropy']

    def generate_replywords(self, keys=None):
        if keys is None:
            keys = []
        replies = []
        with self.get_context(self.forward) as context:
            start = True
            while True:
                if start:
                    symbol = context.seed(keys)
                    start = False
                else:
                    symbol = context.babble(keys, replies)
                if symbol in (self.error_symbol, self.end_symbol):
                    break
                replies.append(self.dictionary[symbol])
                context.update(symbol)
        with self.get_context(self.backward) as context:
            if replies:
                for i in range(min([(len(replies) - 1), self.order]), -1, -1):
                    context.update(self.dictionary.index(replies[i]))
            while True:
                symbol = context.babble(keys, replies)
                if symbol in (self.error_symbol, self.end_symbol):
                    break
                replies.insert(0, self.dictionary[symbol])
                context.update(symbol)

        return replies

    def make_keywords(self, words):
        keys = Dictionary()
        for word in words:
            try:
                word = self.swapwords[word]
            except KeyError:
                pass
            if (self.dictionary.find_word(word) != self.error_symbol and
                                                     word[0].isalnum() and
                word not in self.banwords and word not in self.auxwords
                                             and word not in keys):
                keys.append(word)

        if keys:
            for word in words:
                try:
                    word = self.swapwords[word]
                except KeyError:
                    pass
                if (self.dictionary.find_word(word) != self.error_symbol and
                                                     word[0].isalnum() and
                    word in self.auxwords and word not in keys):
                    keys.append(word)

        return keys

    def add_key(self, keys, word):
        if (self.dictionary.find_word(word) != self.error_symbol and
            self.banwords.find_word(word) == self.error_symbol and
            self.auxwords.find_word(word) == self.error_symbol):
            keys.add_word(word)

    def sync(self):
        self.db.sync()

    def close(self):
        if not self.closed:
            print('Closing database')
            self.db.close()
            self.closed = True

    def __del__(self):
        try:
            self.close()
        except:
            pass


class MegaHAL2(object):

    def __init__(self, order=None, brainfile=None, timeout=None):
        if order is None:
            order = DEFAULT_ORDER
        if brainfile is None:
            brainfile = DEFAULT_BRAINFILE
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        self.__brain = Brain(order, brainfile, timeout)
        self._megahal__brain = self.__brain

    @property
    def banwords(self):
        """This is a list of words which cannot be used as keywords"""
        return self.__brain.banwords

    @property
    def auxwords(self):
        """This is a list of words which can be used as keywords only in order
         to supplement other keywords"""
        return self.__brain.auxwords

    @property
    def swapwords(self):
        """The word on the left is changed to the word on the right
        when used as a keyword"""
        return self.__brain.swapwords

    def train(self, file):
        """Train the brain with textfile, each line is a phrase"""
        with open(file, 'rb') as fp:
            for line in fp:
                line = line.strip()
                if line and not line.startswith('#'):
                    self.learn(line)

    def learn(self, phrase):
        """Learn from phrase"""
        self.__brain.communicate(phrase, reply=False)

    def get_reply(self, phrase):
        """Get a reply based on the phrase"""
        return self.__brain.communicate(phrase)

    def get_reply_nolearn(self, phrase):
        """Get a reply without updating the database"""
        return self.__brain.communicate(phrase, learn=False)

    def interact(self):
        """Have a friendly chat session.. ^D to exit"""
        while True:
            try:
                phrase = input('>>> ')
            except EOFError:
                break
            if phrase:
                print((self.get_reply(phrase)))

    def sync(self):
        """Flush any changes to disk"""
        self.__brain.sync()

    def close(self):
        """Close database"""
        self.__brain.close()
