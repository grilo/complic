#!/usr/bin/env python

import logging
import re


class Matcher(object):

    def __init__(self, registry):
        self._lics = {}
        for k, regex in registry.items():
            if not k in self._lics:
                self._lics[k] = {}
            self._lics[k]['short'] = re.compile(regex['short'], re.DOTALL)
            self._lics[k]['long'] = re.compile(regex['long'], re.DOTALL)

    def from_file(self, file_path):
        with open(file_path, 'r') as license_file:
            return self.from_string(license_file.read())

    def from_string(self, string):
        """Return an iterator with all licenses which match the given string."""
        lics = set()
        for key, regex in self._lics.items():
            if regex['short'].match(string) or \
                regex['long'].match(string):
                logging.debug("Match for: %s", key)
                lics.add(key)
            else:
                lic = 'Uknown (%s)' % (string.splitlines()[0])
                lics.add(lic)
        return lics
