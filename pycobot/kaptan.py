# -*- coding: utf8 -*-
"""
    kaptan
    ~~~~~~

    configuration parser.

    :copyright: (c) 2013 by the authors and contributors (See AUTHORS file).
    :license: BSD, see LICENSE for more details.
"""

import os
from collections import Mapping, Sequence
import json

SENTINEL = object()

HANDLER_EXT = {
#    'ini': 'ini',
#    'conf': 'ini',
#    'yaml': 'yaml',
#    'yml': 'yaml',
    'json': 'json',
    'conf': 'json',
#    'py': 'file',
}


class BaseHandler(object):
    """Base class for data handlers."""

    def load(self, data):
        raise NotImplementedError

    def dump(self, data):
        raise NotImplementedError


class DictHandler(BaseHandler):

    def load(self, data):
        return data

    def dump(self, data):
        return data


class JsonHandler(BaseHandler):

    def load(self, data):
        return json.loads(data)

    def dump(self, data, **kwargs):
        return json.dumps(data, **kwargs)


class Kaptan(object):

    HANDLER_MAP = {
        'json': JsonHandler,
        'dict': DictHandler,
#        'yaml': YamlHandler,
#        'file': FileHandler,
#        'ini': IniHandler,
    }

    def __init__(self, handler=None):
        self.configuration_data = dict()
        self.handler = None
        if handler:
            self.handler = self.HANDLER_MAP[handler]()

    def merge_dictionary(self, dst, src):
        stack = [(dst, src)]
        while stack:
            current_dst, current_src = stack.pop()
            for key in current_src:
                if key not in current_dst:
                    current_dst[key] = current_src[key]
                else:
                    if isinstance(current_src[key], dict) and isinstance(
                                                    current_dst[key], dict):
                        stack.append((current_dst[key], current_src[key]))
                    else:
                        current_dst[key] = current_src[key]
        return dst

    def put(self, key, value):
        return self.upsert(key, value)

    def upsert(self, key, value):
        parts = key.split('.')

        def pack(parts):
            if len(parts) == 1:
                return {parts[0]: value}
            elif len(parts):
                return {parts[0]: pack(parts[1:])}
            return parts
        f = pack(parts)

        self.configuration_data = self.merge_dictionary(self.configuration_data,
                                                                             f)
        return self

    def import_config(self, value):
        if not isinstance(value, dict) and os.path.isfile(value):
            if not self.handler:
                try:
                    key = HANDLER_EXT.get(os.path.splitext(value)[1][1:], None)
                    self.handler = self.HANDLER_MAP[key]()
                except:
                    raise RuntimeError("Unable to determine handler")
            with open(value) as f:
                value = f.read()
        elif isinstance(value, dict):  # load python dict
            self.handler = self.HANDLER_MAP['dict']()

        self.configuration_data = self.handler.load(value)
        return self

    def _get(self, key):
        current_data = self.configuration_data

        for chunk in key.split('.'):
            if isinstance(current_data, Mapping):
                current_data = current_data[chunk]
            elif isinstance(current_data, Sequence):
                chunk = int(chunk)

                current_data = current_data[chunk]
            else:
                # A scalar type has been found
                return current_data

        return current_data

    def get(self, key=None, default=SENTINEL):
        if not key:  # .get() or .get(''), return full config
            return self.export('dict')

        try:
            try:
                return self._get(key)
            except KeyError:
                raise KeyError(key)
            except ValueError:
                raise ValueError("Sequence index not an integer")
            except IndexError:
                raise IndexError("Sequence index out of range")
        except (KeyError, ValueError, IndexError):
            if default is not SENTINEL:
                return default
            raise

    def export(self, handler=None, **kwargs):
        if not handler:
            handler_class = self.handler
        else:
            handler_class = self.HANDLER_MAP[handler]()

        return handler_class.dump(self.configuration_data, **kwargs)

    def __handle_default_value(self, key, default):
        if default == SENTINEL:
            raise KeyError(key)
        return default
