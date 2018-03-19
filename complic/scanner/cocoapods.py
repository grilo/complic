#!/usr/bin/env python
"""
    Scan all Podfile.lock files.
"""

import logging
import json
import re
import distutils

from complic.utils import shell

from . import base
from . import npm


class Scanner(base.Scanner):
    """Scan all Podfile.lock files.

    Depends on having "pod" executable in the PATH."""

    def __init__(self):
        super(Scanner, self).__init__()

        if not distutils.spawn.find_executable('pod'):
            logging.error("Unable to find 'pod' executable in PATH.")

        self.register_handler(re.compile(r'.*/Podfile.lock$'),
                              Scanner.handle_podfile)

    @staticmethod
    def get_podspec(podname):
        """Returns the JSON structure of the given pod name.

        This should have a "version" parameter for completeness sake, but
        I don't know how to query for specific versions :(
        """
        command = "pod spec cat '%s'" % (podname)
        return_code, out, _ = shell.cmd(command)
        if return_code != 0:
            if 'Unable to find a pod with name matching' in out:
                logging.error("Make sure you have 'pod setup' executed.")
            return {}
        return json.loads(out)

    @staticmethod
    def get_ids_from_podfile(string):
        """Returns a list of <identifiers> found in the given string.

        An <identifier> is a string composed of:
            technology:name:version

        Example:
            pod:AFNetworking:2.3.0

        """
        identifiers = set()
        regex = re.compile(r'\s+- ([A-Za-z\/-_\.0-9]+)\s*\([><=~ ]*([0-9\.]+)\)')
        for line in string.splitlines():
            match = regex.match(line)
            if not match:
                continue
            name = match.group(1).split('/')[0]
            version = match.group(2)
            identifiers.add(':'.join(['pod', name, version]))
        return identifiers

    @staticmethod
    def handle_podfile(file_path):
        """Handles Podfile.lock file.

        We should be doing real parsing with a YAML parser, but we just do
        basic stuff instead."""

        dependencies = []

        for identifier in Scanner.get_ids_from_podfile(open(file_path, 'r').read()):
            dependency = base.Dependency(identifier, file_path)
            spec = Scanner.get_podspec(identifier.split(':')[1])
            for lic in npm.Scanner.get_licenses(spec):
                dependency.licenses.add(lic)
            dependencies.append(dependency)

        return dependencies
