# -*- coding: utf-8 -*-
import logging
import _thread
import socket
import re
import time
from . import numerics
from . import features

_rfc_1459_command_regexp = re.compile("^(:(?P<prefix>[^ ]+) +)?" +
    "(?P<command>[^ ]+)( *(?P<argument> .+))?")


class IRCClient:
    # Defaults..
    server = None    # Dirección del servidor IRC
    port = 6667      # Puerto al que se conectará
    nickname = "Groo"    # Nick
    ident = nickname
    gecos = "-"      # "Nombre real"
    ssl = False
    msgdelay = 0.5   # Demora en el envío de mensajes (para no caer por flood)
    reconnects = 10  # Intentos de reconectarse desde la ultima conexion fallida
    reconncount = 0  # Números de intentos de reconección realizados.

    features = None
    buffer = None
    connected = False
    logger = None
    socket = None
    handlers = {}
    queue = []

    def __init__(self, sid):
        self.logger = logging.getLogger('bearded-potato-' + sid)
        self.buffer = LineBuffer()
        self.features = features.FeatureSet()
        #self.addhandler("pubmsg", self._pubmsg)

    def configure(self, server=server, port=port, nick=nickname, ident=nickname,
                gecos=gecos, ssl=ssl, msgdelay=msgdelay, reconnects=reconnects):
        self.server = server
        self.port = port
        self.nickname = nick
        self.ident = nick
        self.gecos = gecos
        self.ssl = ssl
        self.msgdelay = msgdelay
                
    def connect(self):
        """ Connects to the IRC server. """
        self.logger.info("Conectando a {0}:{1}".format(self.server, self.port))
        try:
            self.socket = socket.create_connection((self.server, self.port))
        except socket.error as err:
            self.logger.error("No se pudo conectar a {0}:{1}: {2}"
                .format(self.server, self.port, err))
            return 1

        self.connected = True
        
        # Iniciamos la cola de envío
        _thread.start_new_thread(self._process_queue, ())
        
        # Iniciamos el bucle de recepción
        _thread.start_new_thread(self._process_forever, ())

        self._fire_event(Event("connect", None, None))
        
        # Nos identificamos..
        self.user(self.ident, self.gecos)
        self.nick(self.nickname)

    def _process_forever(self):
        while self.connected:
            self._process_data()
        self.reconncount += 1
        if self.reconncount <= self.reconnects:
            self.connect()
            
    def _processline(self, line):
        prefix = None
        command = None
        arguments = None
        self._fire_event(Event("all_raw_messages",
                                 self.server,
                                 None,
                                 [line]))

        m = _rfc_1459_command_regexp.match(line)
        if m.group("prefix"):
            prefix = m.group("prefix")

        if m.group("command"):
            command = m.group("command").lower()

        if m.group("argument"):
            a = m.group("argument").split(" :", 1)
            arguments = a[0].split()
            if len(a) == 2:
                arguments.append(a[1])

        # Translate numerics into more readable strings.
        command = numerics.numerics.get(command, command)

        if command == "nick":
            if NickMask(prefix).nick == self.nickname:
                self.nickname = arguments[0]
        elif command == "welcome":
            self.join("#cobot")
            
            # Record the nickname in case the client changed nick
            # in a nicknameinuse callback.
            self.nickname = arguments[0]
        elif command == "featurelist":
            self.features.load(arguments)

        if command in ["privmsg", "notice"]:
            target, message = arguments[0], arguments[1]
            messages = _ctcp_dequote(message)

            if command == "privmsg":
                if is_channel(target):
                    command = "pubmsg"
            else:
                if is_channel(target):
                    command = "pubnotice"
                else:
                    command = "privnotice"

            for m in messages:
                if isinstance(m, tuple):
                    if command in ["privmsg", "pubmsg"]:
                        command = "ctcp"
                    else:
                        command = "ctcpreply"

                    m = list(m)
                    self.logger.debug("command: %s, source: %s, target: %s, "
                        "arguments: %s", command, prefix, target, m)
                    self._fire_event(Event(command, NickMask(prefix), target,
                         m))
                    if command == "ctcp" and m[0] == "ACTION":
                        self._fire_event(Event("action", prefix, target,
                             m[1:]))
                else:
                    self.logger.debug("command: %s, source: %s, target: %s, "
                        "arguments: %s", command, prefix, target, [m])
                    self._fire_event(Event(command, NickMask(prefix), target,
                        [m]))
        else:
            target = None

            if command == "quit":
                arguments = [arguments[0]]
            elif command == "ping":
                # Hardcoded pong :D
                self.pong(arguments[0])
                target = arguments[0]
            else:
                target = arguments[0]
                arguments = arguments[1:]

            if command == "mode":
                if not is_channel(target):
                    command = "umode"

            self.logger.debug("command: %s, source: %s, target: %s, "
                "arguments: %s", command, prefix, target, arguments)
            self._fire_event(Event(command, NickMask(prefix), target,
                arguments))
                
    def _process_data(self):
        if not self.connected:
            return 1
        try:
            reader = getattr(self.socket, 'read', self.socket.recv)
            new_data = reader(2 ** 14)
        except socket.error:
            # The server hung up.
            self.disconnect("Connection reset by peer")
            return False
        if not new_data:
            # Read nothing: connection must be down.
            self.disconnect("Connection reset by peer")
            return False

        self.buffer.feed(new_data)

        for line in self.buffer:
            if not line:
                continue
            self.logger.debug(line)
            self._processline(line)
        
    def _process_queue(self):
        while True:
            if self.connected is False:
                return 0
            for stuff in self.queue:
                time.sleep(self.msgdelay)
                self.send_stuff(stuff)
            self.queue = []
            time.sleep(self.msgdelay)

    def _fire_event(self, event):
        try:
            self.handlers[event.type]
            for i in self.handlers[event.type]:
                i[callback](self, event)
        except:
            pass

    # Registers a bot handler.
    # action = Command/translated numeric that will trigger the handler
    # callback = Function to call back (Parameters: this class and a event object)
    # blocking = If true, the handler won't be executed in a thread
    def addhandler(self, action, callback, blocking=False):
        try:
            self.handlers[action]
        except:
            self.handlers[action] = []
        self.handlers[action].append({'blocking': blocking, 
                                      'action': action,
                                      'callback': callback})
        
    def send(self, raw, urgent=False):
        if urgent is False:
            self.queue.append(raw)
        else:
            self.send_stuff(raw)

    def send_stuff(self, stuff):
        bytes_ = stuff.encode('utf-8') + b'\r\n'
        if len(bytes_) > 512:
            self.logger.warning("Se ha intentado enviar un mensaje muy largo!")
        try:
            self.socket.send(bytes_)
            self.logger.debug("TO SERVER: {0}".format(stuff))
        except socket.error:
            # Ouch!
            self.disconnect("Connection reset by peer.")
    
    def disconnect(self, message):
        self.reconncount = 100000  # :D
        if not self.connected:
            return

        self.connected = False

        self.quit(message)

        try:
            self.socket.shutdown(socket.SHUT_WR)
            self.socket.close()
        except socket.error:
            pass
        self.logger.info("Desconectado del servidor: {0}".format(message))
        self._fire_event(Event("disconnect", None, None))
        del self.socket
    
    ### IRC Commands ###
    
    def user(self, user, realname):
        self.send("USER {0} * * :{1}".format(user, realname), True)
    
    def nick(self, nick):
        self.send("NICK {0}".format(nick), True)
    
    def quit(self, reason):
        self.send("QUIT :{0}".format(reason), True)
    
    def pong(self, param):
        self.send("PONG :{0}".format(param))
    
    def join(self, channels):
        self.send("JOIN {0}".format(channels))


class Event(object):
    def __init__(self, type, source, target, arguments=None):
        self.type = type
        self.source = source
        self.source2 = source
        self.target = target
        if arguments is None:
            arguments = []
        self.arguments = arguments
        if type == "privmsg" or type == "pubmsg" or type == "ctcpreply" or type\
        == "ctcp" or type == "pubnotice" or type == "privnotice":
            if not is_channel(target):
                self.target = parse_nick(source)[1]
            if not is_channel(source):
                self.source = parse_nick(source)[1]
            self.splitd = arguments[0].split()


class LineBuffer(object):
    line_sep_exp = re.compile(b'\r?\n')

    def __init__(self):
        self.buffer = b''

    def feed(self, byte):
        self.buffer += byte

    encoding = 'utf-8'
    errors = 'replace'

    def lines(self):
        return (line.decode(self.encoding, self.errors)
            for line in self._lines())

    def _lines(self):
        lines = self.line_sep_exp.split(self.buffer)
        # save the last, unfinished, possibly empty line
        self.buffer = lines.pop()
        return iter(lines)

    def __iter__(self):
        return self.lines()

    def __len__(self):
        return len(self.buffer)


def is_channel(string):
    """Check if a string is a channel name.

    Returns true if the argument is a channel name, otherwise false.
    """
    return string and string[0] in "#&+!"


def parse_nick(name):
    """ parse a nickname and return a tuple of (nick, mode, user, host)

    <nick> [ '!' [<mode> = ] <user> ] [ '@' <host> ]
    """

    try:
        nick, rest = name.split('!')
    except ValueError:
        return (name, None, None, None)
    try:
        mode, rest = rest.split('=')
    except ValueError:
        mode, rest = None, rest
    try:
        user, host = rest.split('@')
    except ValueError:
        return (name, mode, rest, None)

    return (name, nick, mode, user, host)

_LOW_LEVEL_QUOTE = "\020"
_CTCP_LEVEL_QUOTE = "\134"
_CTCP_DELIMITER = "\001"
_low_level_mapping = {
    "0": "\000",
    "n": "\n",
    "r": "\r",
    _LOW_LEVEL_QUOTE: _LOW_LEVEL_QUOTE
}

_low_level_regexp = re.compile(_LOW_LEVEL_QUOTE + "(.)")


def _ctcp_dequote(message):
    """[Internal] Dequote a message according to CTCP specifications.

    The function returns a list where each element can be either a
    string (normal message) or a tuple of one or two strings (tagged
    messages).  If a tuple has only one element (ie is a singleton),
    that element is the tag; otherwise the tuple has two elements: the
    tag and the data.

    Arguments:

        message -- The message to be decoded.
    """

    def _low_level_replace(match_obj):
        ch = match_obj.group(1)

        # If low_level_mapping doesn't have the character as key, we
        # should just return the character.
        return _low_level_mapping.get(ch, ch)

    if _LOW_LEVEL_QUOTE in message:
        # Yup, there was a quote.  Release the dequoter, man!
        message = _low_level_regexp.sub(_low_level_replace, message)

    if _CTCP_DELIMITER not in message:
        return [message]
    else:
        # Split it into parts.  (Does any IRC client actually *use*
        # CTCP stacking like this?)
        chunks = message.split(_CTCP_DELIMITER)

        messages = []
        i = 0
        while i < len(chunks) - 1:
            # Add message if it's non-empty.
            if len(chunks[i]) > 0:
                messages.append(chunks[i])

            if i < len(chunks) - 2:
                # Aye!  CTCP tagged data ahead!
                messages.append(tuple(chunks[i + 1].split(" ", 1)))

            i = i + 2

        if len(chunks) % 2 == 0:
            # Hey, a lonely _CTCP_DELIMITER at the end!  This means
            # that the last chunk, including the delimiter, is a
            # normal message!  (This is according to the CTCP
            # specification.)
            messages.append(_CTCP_DELIMITER + chunks[-1])

        return messages


class NickMask(str):
    @classmethod
    def from_params(cls, nick, user, host):
        return cls('{nick}!{user}@{host}'.format(**vars()))

    @property
    def nick(self):
        return self.split("!")[0]

    @property
    def userhost(self):
        return self.split("!")[1]

    @property
    def host(self):
        return self.split("@")[1]

    @property
    def user(self):
        return self.userhost.split("@")[0]
