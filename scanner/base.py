#!/usr/bin/env python

import logging
import re


class Scanner(object):

    def __init__(self):
        self.handlers = {}
        self.register_handler(re.compile('ONLY_EXAMPLE'),
                              self.example_handler)

    def register_handler(self, regex, callback):
        self.handlers[regex] = callback

    def example_handler(self, file_path):
        pass

    def scan(self, filelist):
        logging.info("Scanning with: %s", self.__module__)
        dependencies = []
        for f in filelist:
            for regex, handler in self.handlers.items():
                if regex.match(f):
                    for dependency in handler(f):
                        dependency.scanner = self.__class__.__module__.split('.')[-1]
                        dependencies.append(dependency)
        logging.info("Apps found: %i", len(dependencies))
        return dependencies


class Dependency(object):

    def __init__(self, *args, **kwargs):
        self._licenses = set()
        for k, v in kwargs.items():
            if not k in self.__dict__:
                setattr(self, '_' + k, v)

    @property
    def identifier(self):
        if not self._id:
            return self.path
        return self._id

    @identifier.setter
    def identifier(self, value):
        self._id = value

    @property
    def licenses(self):
        return self._licenses

    @licenses.setter
    def licenses(self, value):
        self._licenses = value

    def __repr__(self):
        try:
            getattr(self, 'licenses')
        except AttributeError:
            print self.path
        if not self.licenses:
            return 'Unknown'
        return ','.join(self.licenses)
