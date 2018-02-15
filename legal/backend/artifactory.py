#!/usr/bin/env python

import logging
import re
import json

import requests

import utils.cache
import legal.backend.base
import legal.exceptions


class Cache(utils.cache.File):

    def __init__(self, base_url, uname, passwd):
        super(Cache, self).__init__('artifactory')
        self.url = base_url + '/artifactory/ui/licenses/crud'
        self.uname = uname
        self.passwd = passwd
    def refresh(self):
        return requests.get(self.url, auth=(self.uname, self.passwd)).text

class Registry(legal.backend.base.Registry):
    """Returns all Artifactory licenses, built-in cache mechanism.

    Handles like an immutable dictionary.

    Note that we're using a "non-public" API of artifactory.
    """

    def __init__(self, base_url='http://artifactory:8080', username=None, password=None):
        super(Registry, self).__init__()
        self.cache = {}
        for lic in json.loads(Cache(base_url, username, password).get()):
            self.cache[lic['name']] = lic['approved']

    def is_approved(self, license):
        if license not in self.cache.keys():
            raise legal.exceptions.UnknownLicenseError
        return self.cache[license]


class SPDX(legal.backend.base.SPDX):

    def __init__(self, base_url='http://artifactory:8080', username=None, password=None):
        super(SPDX, self).__init__()
        self.cache = json.loads(Cache(base_url, username, password).get())

        # Build regex list
        self.licenses = {}
        for lic in self.cache:
            regex = lic.get('regexp', None)
            if regex:
                self.licenses[lic['name']] = {
                    'regexp': re.compile(regex, re.IGNORECASE),
                    'status': lic['status'],
                }

    def match(self, string):
        for lic, props in self.licenses.items():
            if props['regexp'].match(string):
                logging.debug("SPDX (%s) found for: %s", lic, string)
                return lic
        raise legal.exceptions.UnknownLicenseError
