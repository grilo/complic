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
        required = ['name', 'version']
        for attribute in required:
            if not attribute in pkgjson.keys():
                raise MalformedBuildFileError("Missing (%s): %s" % (attribute, pkgjson))
        return pkgjson['name'] + ':' + pkgjson['version']

    def __init__(self, *args, **kwargs):
        super(Scanner, self).__init__(*args, **kwargs)

        self.register_handler(re.compile(r'.*/LICENSE.*'),
                              self.handle_license)

        self.register_handler(re.compile(r'.*/package.json$'),
                              self.handle_pkgjson)

    def handle_license(self, file_path):
        logging.debug("Matched license handler: %s", file_path)
        result = scanner.base.Result(file_path)
        for lic in self.license_matcher.from_file(file_path):
            result.licenses.add(lic)
        # If there's a package.json file right next to this one we take it
        # as the identifier. Otherwise, use the file's path.
        pkgjson_path = os.path.join(os.path.dirname(file_path), 'package.json')
        if os.path.isfile(pkgjson_path):
            result.identifier = Scanner._get_id(Scanner._read_pkgjson(pkgjson_path))
        return result

    def handle_pkgjson(self, file_path):
        logging.debug("Matched package.json handler: %s", file_path)
        result = scanner.base.Result(file_path)
        pkgjson = Scanner._read_pkgjson(file_path)
        result.identifier = Scanner._get_id(pkgjson)

        # Normalize the naming if required
        if 'licenses' in pkgjson.keys():
            pkgjson['license'] = pkgjson['licenses']

        if 'license' in pkgjson.keys():
            if isinstance(pkgjson['license'], str) or isinstance(pkgjson['license'], unicode):
                result.licenses = self.license_matcher.from_string(pkgjson['license'])
            else:
                for license in pkgjson['license']:
                    for lic in self.license_matcher.from_string(license['type']):
                        result.licenses.add(lic)

        return result
