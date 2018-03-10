#!/usr/bin/env python

import os
import json
import re
import logging

import complic.licenses.exceptions


class Normalizer(object):
    """Normalize license names.


    Since many people get very creative with the way they license their
    software, we try normalizing things such as:
            GPL-2
        and
            GPLv2
    usually into its SPDX definition (if it exists). We keep track of all
    known licenses in our own inventory since the SPDX index is extensive
    but still limited.
    """

    def __init__(self, licenses=None):
        """The license inventory file <licenses> has the mandatory structure:

        unique_lic_identifier:
            'regex': some([regex]expression)
        """
        self.licenses = {}
        if not licenses:
            inventory_path = os.path.join(os.path.dirname(__file__),
                                          'inventory.json')
            with open(inventory_path, 'r') as inventory:
                for lic, props in json.loads(inventory.read()).items():
                    props['regexp'] = re.compile(props['regexp'])
                    self.licenses[lic] = props

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
        raise complic.licenses.exceptions.UnknownLicenseError
