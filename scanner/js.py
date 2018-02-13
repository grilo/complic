#!/usr/bin/env python

import logging
import json
import re
import os

import scanner.base


class Scanner(scanner.base.Scanner):

    @staticmethod
    def get_licenses(pkgjson):
        lics = []
        # Normalize the naming if required
        if 'licenses' in pkgjson.keys():
            pkgjson['license'] = pkgjson['licenses']
        if 'license' in pkgjson.keys():
            # Normalize the type to list
            if isinstance(pkgjson['license'], str) or \
                isinstance(pkgjson['license'], unicode):
                pkgjson['license'] = [pkgjson['license']]

            for license in pkgjson['license']:
                if isinstance(license, dict):
                    lics.append(license['type'])
                else:
                    lics.append(license)
        return lics

    def __init__(self, *args, **kwargs):
        super(Scanner, self).__init__(*args, **kwargs)

        self.register_handler(re.compile(r'.*/package.json$'),
                              self.handle_pkgjson)

    def handle_pkgjson(self, file_path):
        logging.debug("Matched package.json handler: %s", file_path)

        pkgjson = json.loads(open(file_path, 'r').read())

        name = pkgjson.get('name', '<none>')
        version = pkgjson.get('version', '<none>')

        dependency = scanner.base.Dependency(file_path)
        dependency.identifier = ':'.join([name, version])

        # Normalize the naming if required
        if 'licenses' in pkgjson.keys():
            pkgjson['license'] = pkgjson['licenses']

        for lic in Scanner.get_licenses(pkgjson):
            dependency.licenses.add(self.license_matcher.match(lic))

        return [dependency]
