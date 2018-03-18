#!/usr/bin/env python

"""
    Base module for all scanners.

    The "scan" method should be left alone, everything else should be overriden.
"""

import logging
import re


class Scanner(object):
    """
        Scans a list of files, invoking the corresponding handler for each one.
    """

    def __init__(self):
        self.handlers = {}

    def register_handler(self, regex, callback):
        """Handler is a simple regex-based callback.

        If the file matches the regex, the callback is invoked.
        """
        self.handlers[regex] = callback

    def scan(self, filelist):
        """This should be left alone.

        The interface used by the logic engine to invoke all scanners.
        """
        logging.info("Scanning with: %s", self.__module__)
        dependencies = []
        for path in filelist:
            for regex, handler in self.handlers.items():
                if not regex.match(path):
                    continue
                for dependency in handler(path):
                    dependencies.append(dependency)
        logging.info("Dependencies collected: %i", len(dependencies))
        return dependencies


class Dependency(object):
    """Represents a dependency.

    A dependency must have:
        identifier (a unique name to represent the module).
        licenses (a set of strings).

    We add many more properties for future compatibility, but they aren't
    really being used.
    """

    def __init__(self, identifier, path):
        # Identifier for this dependency. The same dependency may show up in
        # multiple places in the same project
        self.identifier = identifier
        # The file we extracted this dependency information from.
        self.path = path

        """
        Some modules might have more than one license. It also represents the
        fact that the same module might be caught twice (perhaps with different
        versions) and this ensures no information is lost.
        """
        self.licenses = set()

    def __repr__(self): # pragma: nocover
        """This is only used for debugging."""
        lics = set('Unknown')
        if self.licenses:
            lics = self.licenses
        return self.identifier + " " + ','.join(lics)
