#!/usr/bin/env python

"""
Backend for Artifactory: https://jfrog.com/artifactory/
The licensing control feature may be behind the PRO version.

The backend contract is:
    Registry class
        (bool) is_approved(license_string)

    SPDX class
        (string) match(license_string)
        Returns the SPDX definition of the license.

    Note: the naming is a bit confusing, it's not directly related with the
    SPDX definition of the licenses. It works with any kind of license as long
    as whatever the <match> method returns is recognized by the <is_approved>
    method.
"""

import logging
import re
import json

import requests

import complic.utils.cache
import complic.backend.exceptions


class Cache(complic.utils.cache.File):
    """Cache the REST call."""

    def __init__(self, url, uname, passwd):
        """The default endpoint used to retrieve licensing information is
        not actually documented."""
        super(Cache, self).__init__('artifactory')
        self.url = url
        self.uname = uname
        self.passwd = passwd

    def refresh(self):
        return requests.get(self.url, auth=(self.uname, self.passwd)).text

class Registry(object):
    """Returns all Artifactory licenses, built-in cache mechanism.

    Handles like an immutable dictionary.

    Note that we're using a "non-public" API of artifactory.
    """

    def __init__(self, config):
        super(Registry, self).__init__()
        self.config = config
        self.cache = {}
        for lic in json.loads(Cache(config.ARTIFACTORY_ENDPOINT,
                                    config.ARTIFACTORY_USERNAME,
                                    config.ARTIFACTORY_PASSWORD).get()):
            self.cache[lic['name']] = lic['approved']

    def is_approved(self, license_string):
        """
            Given a license string, returns whether the license is approved
            for use or not. Although this class caches the information, it
            doesn't actually manage it and depends on an external backend to
            do that (in this case, Artifactory).

            Example:
                >>> is_approved('BSD')
                True

                >>> is_approved('AGPL')
                False
        """
        if license_string not in self.cache.keys():
            raise complic.backend.exceptions.UnknownLicenseError
        return self.cache[license_string]


class SPDX(object):
    """Artifactory's license control is a very simple regex engine.

    We collect the three values that matter to use: the name of the
    license, the regular expression and whether it's approved or not.
    """

    def __init__(self, config):
        super(SPDX, self).__init__()
        self.cache = json.loads(Cache(config.ARTIFACTORY_ENDPOINT,
                                      config.ARTIFACTORY_USERNAME,
                                      config.ARTIFACTORY_PASSWORD).get())
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
        """Finds the first regex that matches and returns its "name".

        If there are no matches, an exception is thrown.

        Example:
            >>> match('Licensed with BSD 2-Clause')
            BSD-2

            >>> match('This is some unknown license')
            raise UnknownLicenseError
        """
        for lic, props in self.licenses.items():
            if props['regexp'].match(string):
                logging.debug("SPDX (%s) found for: %s", lic, string)
                return lic
        raise complic.backend.exceptions.UnknownLicenseError
