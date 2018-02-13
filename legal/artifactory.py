#!/usr/bin/env python

import logging
import re
import json

import requests

import utils.cache


class Cache(utils.cache.Remote):
    """Returns all Artifactory licenses, built-in cache mechanism.

    Handles like an immutable dictionary.

    Note that we're using a "non-public" API of artifactory.
    """

    def __init__(self, url='http://artifactory:8080/artifactory/ui/licenses/crud'):
        super(Cache, self).__init__(url=url, name='artifactory')

    def _refresh(self):
        return json.loads(open('/home/grilo/projects/complic/jaylics', 'r').read())


class Matcher(object):

    def __init__(self, registry):
        # Build regex list
        self.licenses = {}
        for lic in registry:
            regex = lic.get('regexp', None)
            if regex:
                self.licenses[lic['name']] = re.compile(regex, re.IGNORECASE)

    def match(self, string):
        matches = []
        for lic, regex in self.licenses.items():
            if regex.match(string):
                matches.append(lic)
        if not matches:
            matches.append('UNKNOWN')
        print "Matches for [%s] %s" % (string, ','.join(matches))
        return matches[0]
