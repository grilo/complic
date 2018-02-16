#!/usr/bin/env python

import logging
import re
import os
import subprocess
import shlex

import complic.scanner.base


class Scanner(complic.scanner.base.Scanner):

    def __init__(self):
        super(Scanner, self).__init__()

        self.register_handler(re.compile(r'.*/pom.xml$'),
                              Scanner.handle_pom)


    @staticmethod
    def handle_pom(file_path):
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
            except subprocess.CalledProcessError as e:
                logging.error("Something went wrong when running: %s", command)
                return []

        return Scanner.parse_thirdparty(thirdparty)

    @staticmethod
    def parse_thirdparty(thirdparty):
        regex = re.compile(r'\s(\(.*\)) (\w+.*) (\(.*\))')
        coords_url = re.compile(r'\((.*) - (http.*)\)')
        dependencies = []
        for line in open(thirdparty, 'r').read().splitlines():

            if not line or line.startswith('List'):
                continue

            match = regex.search(line)
            if not match:
                continue
            license = match.group(1).replace('(', '').replace(')', '')
            name = match.group(2)
            coords, url = match.group(3).split(' - ', 1)
            coords = coords.replace('(', '')
            url = url.replace(')', '')

            dependency = complic.scanner.base.Dependency(thirdparty)
            dependency.identifier = 'java:' + coords
            dependency.licenses.add(license)

            dependencies.append(dependency)

        logging.info("Collected (%i) dependencies.", len(dependencies))
        return dependencies
