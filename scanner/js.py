#!/usr/bin/env python

import logging
import json
import re
import os

import scanner.base


class Scanner(scanner.base.Scanner):

    def __init__(self):
        super(Scanner, self).__init__()

        self.register_handler(re.compile(r'.*/package.json$'),
                              Scanner.handle_pkgjson)

    @staticmethod
    def handle_pkgjson(file_path):
        logging.debug("Matched package.json handler: %s", file_path)

        try:
            pkgjson = json.loads(open(file_path, 'r').read())
        except ValueError:
            logging.error("File appears invalid package.json: %s", file_path)
            return []

        name = pkgjson.get('name', '<none>')
        version = pkgjson.get('version', '<none>')

        dependency = scanner.base.Dependency(file_path)
        dependency.identifier = 'js:' + name + ':' + version

        for lic in Scanner.get_licenses(pkgjson):
            dependency.licenses.add(lic)

        return [dependency]

    @staticmethod
    def get_licenses(pkgjson):
        lics = []
        # Normalize the naming if required
        if 'licenses' in pkgjson.keys():
            pkgjson['license'] = pkgjson['licenses']
        if 'license' in pkgjson.keys():
            # Normalize the type to list
            if not isinstance(pkgjson['license'], list):
                pkgjson['license'] = [pkgjson['license']]

            for lic in pkgjson['license']:
                if isinstance(lic, str) or isinstance(lic, unicode):
                    lics.append(lic)
                else:
                    lics.append(lic['type'])
        return lics

