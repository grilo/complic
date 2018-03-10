#!/usr/bin/env python
"""
    Scan all Podfile.lock files.
"""

import logging
import json
import re

from . import base


class Scanner(base.Scanner):
    """Scan all Podfile.lock files.

    Depends on having "pod" executable in the PATH."""

    def __init__(self):
        super(Scanner, self).__init__()

        self.register_handler(re.compile(r'.*/Podfile.lock$'),
                              Scanner.handle_podfile)

    @staticmethod
    def get_podspec(podname, version=None):
        # I don't know how to query for specific versions :(
        licenses = []
        command = "pod spec cat '%s'" % (podname)
        rc, out, err = complic.utils.shell.cmd(command)
        if rc != 0:
            return {}
        return json.loads(out)

    @staticmethod
    def handle_podfile(file_path):
        """Handles Podfile.lock file.

        We should be doing real parsing with a YAML parser, but we just do
        basic stuff instead."""

        dependencies = []
        regex = re.compile(r'\s - ([A-Za-z\/-_\.0-9]+)\s*\([><=~ ]*([0-9\.]+)\)')

        identifiers = set()

        for line in open(file_path, 'r').read().splitlines():
            match = regex.match(line)
            if not match:
                continue
            name = match.group(1).split('/')[0]
            version = match.group(2)
            identifier = ':'.join(['pod', name, version])

            dependency = base.Dependency(**{'path': file_path})
            dependency.identifier = identifier
            spec = Scanner.get_podspec(name)
            for lic in Scanner.get_licenses(spec):
                dependency.licenses.add(lic)
            dependencies.append(dependency)

        return dependencies

    @staticmethod
    def get_licenses(pkgjson):
        """Pasted from: complic.scanner.npm."""
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
