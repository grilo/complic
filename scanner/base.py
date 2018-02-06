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
        logging.info("Scanning (%i) files with: %s", len(filelist), self.__module__)
        results = []
        for f in filelist:
            for regex, handler in self.handlers.items():
                if regex.match(f):
                    for result in handler(f):
                        results.append(result)
        return results


class Result(object):

    def __init__(self, path):
        self.path = path
        self.technology = None
        self.licenses = set()
        self._id = None

    @property
    def identifier(self):
        if not self._id:
            return self.path
        return self._id

    @identifier.setter
    def identifier(self, value):
        self._id = value

    def merge(self, result):
        basis = None
        if self.identifier.startswith('/'):
            basis = Result(result.path)
            basis.identifier = result.identifier
        else:
            basis = Result(self.path)
            basis.identifier = self.identifier

        basis.licenses = result.licenses.union(self.licenses)
        return basis

    def __repr__(self):
        try:
            getattr(self, 'licenses')
        except AttributeError:
            print self.path
        if not self.licenses:
            return 'Unknown'
        return ','.join(self.licenses)
