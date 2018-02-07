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
        dependencies = []
        for f in filelist:
            for regex, handler in self.handlers.items():
                if regex.match(f):
                    for dependency in handler(f):
                        dependency.scanner = self.__class__.__module__
                        dependencies.append(dependency)
        return dependencies


class Dependency(object):

    def __init__(self, path):
        self.path = path
        self.scanner = None
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

    def merge(self, dependency):
        basis = None
        if self.identifier.startswith('/'):
            basis = Dependency(dependency.path)
            basis.identifier = dependency.identifier
            basis.scanner = dependency.scanner
        else:
            basis = Dependency(self.path)
            basis.identifier = self.identifier
            basis.scanner = self.scanner

        basis.licenses = dependency.licenses.union(self.licenses)
        return basis

    def __repr__(self):
        try:
            getattr(self, 'licenses')
        except AttributeError:
            print self.path
        if not self.licenses:
            return 'Unknown'
        return ','.join(self.licenses)
