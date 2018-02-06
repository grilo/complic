#!/usr/bin/env python

import logging
import re
import os
import subprocess
import shlex

import scanner.base


class Scanner(scanner.base.Scanner):

    def __init__(self, *args, **kwargs):
        super(Scanner, self).__init__(*args, **kwargs)

        self.register_handler(re.compile(r'.*/pom.xml$'),
                              self.handle_pom)

    def handle_pom(self, file_path):
        logging.debug("Matched pom handler: %s", file_path)
        command = "mvn org.codehaus.mojo:license-maven-plugin:1.13"
        command += ":add-third-party -q -B -f %s" % (file_path)
        try:
            subprocess.check_call(shlex.split(command))
        except subprocess.CalledProcessError as e:
            logging.error("Something went wrong when running: %s", command)
            return []

        thirdparty = os.path.join(os.path.dirname(file_path),
                                  'target',
                                  'generated-sources',
                                  'license',
                                  'THIRD-PARTY.txt')
        return self.parse_thirdparty(thirdparty)

    def parse_thirdparty(self, thirdparty):
        logging.debug("Matched THIRDPARTY.txt")
        regex = re.compile(r'\s(\(.*\)) (\w+.*) (\(.*\))')
        coords_url = re.compile(r'\((.*) - (http.*)\)')
        results = []
        for line in open(thirdparty, 'r').read().splitlines():
            if not line:
                continue
            elif line.startswith('List'):
                continue

            match = regex.search(line)
            license = match.group(1)
            name = match.group(2)
            coords, url = match.group(3).split(' - ', 1)
            coords = coords.replace('(', '')
            url = url.replace(')', '')

            result = scanner.base.Result(thirdparty)
            result.identifier = coords
            result.licenses.add(self.license_matcher.name(license))
            result.technology = 'java'

            results.append(result)

        return results
