#!/usr/bin/env python

import logging
import re


class Matcher(object):

    def __init__(self, registry):
        self.registry = registry
        # Build regex list
        self.license_corpus = {}

    def generic(self, string):
        matches = []
        for lic, regex in license_corpus.items():
            if regex.match(string):
                matches.append(lic)
        return matches

    def text(self, string):
        return self.generic(string)

    def url(self, string):
        return self.generic(string)

    def name(self, string):
        return self.generic(string)

    def best(self, string):
        return self.generic(string)
