#!/usr/bin/env python

import logging
import json
import re
import os

import scanner.base
import scanner.exceptions


class Scanner(scanner.base.Scanner):

    @staticmethod
    def _read_pkgjson(file_path):
        return json.loads(open(file_path, 'r').read())

    @staticmethod
    def _get_id(pkgjson):
        coords = [
            'js',
            pkgjson.get('name', 'UnknownName'),
            pkgjson.get('version', 'UnknownVersion'),
        ]
        return ':'.join(coords)

    def __init__(self, *args, **kwargs):
        super(Scanner, self).__init__(*args, **kwargs)

        self.register_handler(re.compile(r'.*/LICENSE.*'),
                              self.handle_license)

        self.register_handler(re.compile(r'.*/package.json$'),
                              self.handle_pkgjson)

    def handle_license(self, file_path):
        logging.debug("Matched license handler: %s", file_path)
        result = scanner.base.Result(file_path)
        lic = self.license_matcher.text(open(file_path, 'r').read())
        result.licenses.add(lic)
        # If there's a package.json file right next to this one we take it
        # as the identifier. Otherwise, use the file's path.
        pkgjson_path = os.path.join(os.path.dirname(file_path), 'package.json')
        if os.path.isfile(pkgjson_path):
            try:
                result.identifier = Scanner._get_id(Scanner._read_pkgjson(pkgjson_path))
            except scanner.exceptions.MalformedBuildFileError:
                logging.error("Ignoring invalid format file: %s", pkgjson_path)
                return
        return [result]

    def handle_pkgjson(self, file_path):
        logging.debug("Matched package.json handler: %s", file_path)
        result = scanner.base.Result(file_path)
        pkgjson = Scanner._read_pkgjson(file_path)
        try:
            result.identifier = Scanner._get_id(pkgjson)
        except scanner.exceptions.MalformedBuildFileError:
            logging.error("Ignoring invalid format file: %s", file_path)
            return

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
                    result.licenses.add(self.license_matcher.name(license['type']))
                    result.licenses.add(self.license_matcher.url(license['url']))
                else:
                    result.licenses.add(self.license_matcher.name(license))

        return [result]
