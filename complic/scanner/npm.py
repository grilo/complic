#!/usr/bin/env python
"""
    Scan all package.json files.
"""

import logging
import json
import re
import distutils.spawn

from . import base


class Scanner(base.Scanner):
    """Scan all package.json files.

    The solution is not very complete. Unless the project has been built
    before (with a full tree of node_modules), the information won't be
    reliable at all.

    Ideally, we would connect to the npm registry itself and download the
    information in case we can't find the package in the node_modules
    directory (of either the project or in the local cache (~/.)).
    """

    def __init__(self):
        super(Scanner, self).__init__()

        if distutils.spawn.find_executable('npm'):
            self.register_handler(re.compile(r'.*/package.json$'),
                                  Scanner.handle_pkgjson)
        else:
            logging.error("Unable to find 'npm' executable in PATH.")


    @staticmethod
    def handle_pkgjson(file_path):
        """Handles package.json file.

        If any parsing errores are found, an empty list is returned."""

        try:
            pkgjson = json.loads(open(file_path, 'r').read())
        except ValueError:
            logging.error("File appears invalid package.json: %s", file_path)
            return []

        name = pkgjson.get('name', '<none>')
        version = pkgjson.get('version', '<none>')

        identifier = 'js:' + name + ':' + version
        dependency = base.Dependency(identifier, file_path)

        for lic in Scanner.get_licenses(pkgjson):
            dependency.licenses.add(lic)

        return [dependency]

    @staticmethod
    def get_licenses(pkgjson):
        """Extract the license information from the package.json.

        What should be a trivial task isn't because that field isn't
        normalized at all and may be formatted differently.

        This is considered legacy: https://docs.npmjs.com/files/package.json

        We account for the following formats:
            - "license": "BSD"

            - "license": ["BSD"]

            - "license": [
                  {
                      "type": "BSD",
                      "url": "http://..."
                  }
              ]
        """
        lics = []
        # Normalize the naming if required
        if 'licenses' in pkgjson.keys():
            pkgjson['license'] = pkgjson['licenses']
        if 'license' in pkgjson.keys():
            # Normalize the type to list
            if not isinstance(pkgjson['license'], list):
                pkgjson['license'] = [pkgjson['license']]

            for lic in pkgjson['license']:
                if isinstance(lic, (str, unicode)):
                    lics.append(lic)
                else:
                    lics.append(lic['type'])
        return lics
