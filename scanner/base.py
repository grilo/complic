#!/usr/bin/env python

import logging
import re


class Scanner(object):

    def __init__(self, license_matcher):
        self.license_matcher = license_matcher
        self.handlers = {}
        self.register_handler(re.compile('ONLY_EXAMPLE'),
                              self.example_handler)

    def register_handler(self, regex, callback):
        self.handlers[regex] = callback

    def example_handler(self, file_path):
        pass

    def scan(self, filelist):
        for f in filelist:
            for lic, handler in self.handlers.items():
                if lic.match(f):
                    yield handler(f)


class Result(object):

    def __init__(self, path):
        self.path = path
        self.licenses = set()
        self.text = ''
        self._id = None

    @property
    def identifier(self):
        if not self._id:
            return self.path
        return self._id

    @identifier.setter
    def identifier(self, value):
        self._id = value

    def __repr__(self):
        try:
            getattr(self, 'licenses')
        except AttributeError:
            print self.path
        if not self.licenses:
            return 'Unknown'
        print self.licenses
        return ','.join(self.licenses)
