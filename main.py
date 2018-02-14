#!/usr/bin/env python

import logging
import argparse
import os
import sys

import utils.fs
import scanner.java
import scanner.js
import scanner.python

import legal.exceptions
import legal.backend.artifactory


if __name__ == '__main__':


    desc = "Collects all licensing information reported by several package managers (mvn, npm, pypi, etc.)."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-v", "--verbose", action="store_true", \
        help="Increase output verbosity")
    parser.add_argument("-d", "--directory", default=os.getcwd(), \
        help="The directory to scan.")
    parser.add_argument("-r", "--report", \
        help="Writes to <:param:> a report in json format.")

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s')
    logging.getLogger().setLevel(getattr(logging, 'INFO'))

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug('Verbose mode activated.')
    if not os.path.isdir(args.directory):
        logging.critical("Specified parameter directory doesn't look like one: %s", args.directory)
        sys.exit(1)

    # Scanners return a list of dependencies and their associated legal blurb.
    scanners = [
        scanner.java.Scanner(),
        scanner.js.Scanner(),
        scanner.python.Scanner(),
    ]

    # We then take that legal blurb and try to find the best SPDX matching
    # designation.
    spdx = legal.backend.artifactory.SPDX('', '', '')

    # We then run that SPDX against the given backend to know if this is
    # considered a compliant license or not.
    registry = legal.backend.artifactory.Registry('', '', '')

    license_identifiers = {}
    unknown_licenses = set()
    for scanner in scanners:
        for dependency in scanner.scan(utils.fs.Find(args.directory).files):
            for license in dependency.licenses:
                try:
                    name = spdx.match(license)
                    if not name in license_identifiers:
                        license_identifiers[name] = set()
                    license_identifiers[name].add(dependency.identifier)
                except legal.exceptions.UnknownLicenseError:
                    unknown_licenses.add(license)


    for lic in unknown_licenses:
        logging.warning("Unknown license: %s", lic)

    # For every non-compliant license, the application will exit with the
    # code 1 + <non-compliant license count>. Exit code 1 is reserved for
    # internal application errors.
    not_approved = 0
    for name, apps in license_identifiers.items():
        state = registry.is_approved(name)
        if not state:
            not_approved += 1
        logging.info("Found (%s) hits for license approved (%s): %s", str(len(apps)).rjust(3), state, name)

    sys.exit(not_approved + 1)
