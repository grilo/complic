#!/usr/bin/env python
"""
    Scans java projects for license information.
"""

import logging
import re
import os
import distutils.spawn

import complic.utils.fs
import complic.utils.shell

from . import base


class Scanner(base.Scanner):
    """
        The handler looks for pom files. We then run the maven plugin
        which produces some THIRD-PARTY files which we will then parse
        for licensing details.
    """

    def __init__(self):
        super(Scanner, self).__init__()

        if distutils.spawn.find_executable('mvn'):
            self.register_handler(re.compile(r'.*/pom.xml$'),
                                  Scanner.handle_pom)
        else:
            logging.error("Unable to find 'mvn' executable in PATH.")

    @staticmethod
    def parse_thirdparty(thirdparty):
        """Parse the strings from THIRD-PARTY files.

        These probably aren't meant to be parsed directly, but the structure
        is regular enough for our use case."""
        regex = re.compile(r'\s(\(.*\)) (\w+.*) (\(.*\))')
        dependencies = {}
        for line in thirdparty.splitlines():

            if not line or line.startswith('List'):
                continue

            match = regex.search(line)
            if not match:
                continue
            license_string = match.group(1).replace('(', '').replace(')', '')
            # match.group(2) is "name" but it's useless
            coords, url = match.group(3).split(' - ', 1)
            coords = coords.replace('(', '')
            url = url.replace(')', '')

            identifier = 'java:' + coords
            if not identifier in dependencies:
                dependencies[identifier] = set()
            dependencies[identifier].add(license_string)

        logging.debug("Dependencies found: %i", len(dependencies))
        return dependencies

    @staticmethod
    def handle_pom(file_path):
        """The licensing plugin which does all the hard work for us.

        This is not very elegant since, in the case of multi-module projects,
        we're running too many times without any need."""

        logging.debug("Matched pom handler: %s", file_path)

        command = "mvn org.codehaus.mojo:license-maven-plugin:1.13"
        command += ":add-third-party -q -B -f %s" % (file_path)
        logging.info("Running license-mvn-plugin on: %s", file_path)
        return_code, _, _ = complic.utils.shell.cmd(command)
        if return_code != 0:
            return []

        deps = []
        for path in complic.utils.fs.Find(os.path.dirname(file_path)).files:
            if not path.endswith('THIRD-PARTY.txt'):
                continue
            string = open(path, 'r').read()
            for identifier, licenses in Scanner.parse_thirdparty(string).items():
                dependency = base.Dependency(identifier, path)
                dependency.licenses = licenses
                deps.append(dependency)

        return deps
