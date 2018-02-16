#!/usr/bin/env python
"""
    Scans java projects for license information.
"""

import logging
import re
import os
import subprocess
import shlex

import complic.scanner.base


class Scanner(complic.scanner.base.Scanner):
    """
        The handler looks for pom files. We then run the maven plugin
        which produces some THIRD-PARTY files which we will then parse
        for licensing details.
    """

    def __init__(self):
        super(Scanner, self).__init__()

        self.register_handler(re.compile(r'.*/pom.xml$'),
                              Scanner.handle_pom)


    @staticmethod
    def handle_pom(file_path):
        """The licensing plugin which does all the hard work for us.

        This is not very elegant since, in the case of multi-module projects,
        we're running too many times without any need."""

        logging.debug("Matched pom handler: %s", file_path)

        thirdparty = os.path.join(os.path.dirname(file_path),
                                  'target',
                                  'generated-sources',
                                  'license',
                                  'THIRD-PARTY.txt')

        if not os.path.isfile(thirdparty):
            command = "mvn org.codehaus.mojo:license-maven-plugin:1.13"
            command += ":aggregate-add-third-party -q -U -B -f %s" % (file_path)
            try:
                logging.info("Running license-mvn-plugin on: %s", file_path)
                subprocess.check_call(shlex.split(command))
            except subprocess.CalledProcessError:
                logging.error("Something went wrong when running: %s", command)
                return []

        return Scanner.parse_thirdparty(thirdparty)

    @staticmethod
    def parse_thirdparty(thirdparty):
        """Parse the THIRD-PARTY files.

        These probably aren't meant to be parsed directly, but the structure
        is regular enough for our use case."""
        regex = re.compile(r'\s(\(.*\)) (\w+.*) (\(.*\))')
        dependencies = []
        for line in open(thirdparty, 'r').read().splitlines():

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

            dependency = complic.scanner.base.Dependency(**{'path': thirdparty})
            dependency.identifier = 'java:' + coords
            dependency.licenses.add(license_string)

            dependencies.append(dependency)

        logging.info("Collected (%i) dependencies.", len(dependencies))
        return dependencies
