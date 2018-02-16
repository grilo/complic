#!/usr/bin/env python
"""
CLI entrypoint and main execution logic.
"""

import logging
import argparse
import os
import sys

import complic.utils.fs
import complic.utils.config
import complic.scanner.java
import complic.scanner.js
import complic.scanner.python
import complic.backend.exceptions
import complic.backend.artifactory


def get_scanners():
    """
        Scanners return a list of complic.scanner.base.Dependency objects
        which contain, among other things, the legal blurb we need.
    """
    return [
        complic.scanner.java.Scanner(),
        complic.scanner.js.Scanner(),
        complic.scanner.python.Scanner(),
    ]

def main():
    """Make the linter happy."""

    desc = "Collect licensing information from package managers (mvn, npm, pypi, etc.)."
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

    config = complic.utils.config.Manager()

    # We then take that legal blurb and try to find the best SPDX matching
    # designation.
    spdx = complic.backend.artifactory.SPDX(config)

    # We then run that SPDX against the given backend to know if this is
    # considered a compliant license or not.
    registry = complic.backend.artifactory.Registry(config)

    license_identifiers = {}
    unknown_licenses = {}
    for scanner in get_scanners():
        for dependency in scanner.scan(complic.utils.fs.Find(args.directory).files):
            for license_string in dependency.licenses:
                try:
                    name = spdx.match(license_string)
                    if not name in license_identifiers:
                        license_identifiers[name] = set()
                    license_identifiers[name].add(dependency.identifier)
                except complic.backend.exceptions.UnknownLicenseError:
                    if not license_string in unknown_licenses:
                        unknown_licenses[license_string] = set()
                    unknown_licenses[license_string].add(dependency.identifier)

    for lic, apps in unknown_licenses.items():
        logging.warning("Apps using unknown license (%s): %i", lic, len(apps))

    # For every non-compliant license, the application will exit with the
    # code 1 + <non-compliant license count>. Exit code 1 is reserved for
    # internal application errors.
    not_approved = 0
    for name, apps in license_identifiers.items():
        if registry.is_approved(name):
            logging.info("Apps using approved license (%s): %i", name, len(apps))
        else:
            not_approved += 1
            logging.error("Apps using unapproved license (%s): %i", name, len(apps))

    sys.exit(not_approved + 1)

if __name__ == '__main__':
    main()
