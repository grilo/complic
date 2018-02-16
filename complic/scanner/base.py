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
        self.register_handler(re.compile('ONLY_EXAMPLE'),
                              self.example_handler)

    def register_handler(self, regex, callback):
        """Handler is a simple regex-based callback.

        If the file matches the regex, the callback is invoked.
        """
        self.handlers[regex] = callback

    def example_handler(self, file_path):
        """Placeholder."""
        pass

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
        logging.info("Apps found: %i", len(dependencies))
        return dependencies


class Dependency(object):
    """Represents a dependency.

    A dependency must have:
        identifier (a unique name to represent the module).
        licenses (a set of strings).

    We add many more properties for future compatibility, but they aren't
    really being used.
    """

    def __init__(self, **kwargs):
        self._licenses = set()
        for key, value in kwargs.items():
            if not key in self.__dict__:
                setattr(self, '_' + key, value)

    @property
    def identifier(self):
        """The module identifier.

            Example:
                >>> dependency.identifier
                java:org.spring.boot:1.0.0

                >>> dependency.identifier
                python:requests:1.0.1a
        """
        if not self._id:
            return self._path # pylint: disable=no-member
        return self._id

    @identifier.setter
    def identifier(self, value):
        self._id = value # pylint: disable=attribute-defined-outside-init

    @property
    def licenses(self):
        """A set of licenses.

        Some modules might have more than one license. It also represents the
        fact that the same module might be caught twice (perhaps with different
        versions) and this ensures no information is lost.
        """
        return self._licenses

    @licenses.setter
    def licenses(self, value):
        self._licenses = value

    def __repr__(self):
        try:
            getattr(self, 'licenses')
        except AttributeError:
            print self._path # pylint: disable=no-member
        if not self.licenses:
            return 'Unknown'
        return ','.join(self.licenses)
