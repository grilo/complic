#!/usr/bin/env python
"""
CLI entrypoint and main execution logic.
"""

import logging
import argparse
import os
import sys
import json
import datetime

import complic.utils.fs

import complic.scanner

import complic.licenses.exceptions
import complic.licenses.regex
import complic.licenses.compat
import complic.licenses.evidence


def get_dependencies(scanners, files):
    dependencies = []
    for scanner in scanners:
        for dependency in scanner.scan(files):
            dependencies.append(dependency)
    return dependencies


def engine(directory, name):
    """Finds all dependencies and corresponding licenses in a given directory.

    Returns a dictionary containing:
         {
            '<license_spdx>': {
                'approved': True|False|None
                'dependencies': [ 'dependency1', 'dependency2' ]
         }
    'approved': None :: license is unknown to the SPDX matcher engine

    SPDX is a fancy name for a license's unique identifier:
        https://spdx.org/
    Example:
        String: Mozilla Public License:
        SPDX: MPL
    """

    # Normalizes strings into the SPDX index (when possible)
    normalizer = complic.licenses.regex.Normalizer()

    # Generate the following map:
    # {
    #   '<license_spdx>': {
    #       'approved': True|False|None
    #       'dependencies': [ 'dependency1', 'dependency2' ]
    #   }


    filelist = complic.utils.fs.Find(directory).files
    report = complic.licenses.evidence.Report(name,
                                              complic.licenses.compat.get())
    dependencies = get_dependencies(complic.scanner.get(), filelist)

    for dependency in dependencies:
        if not dependency.licenses:
            report.add_license('<no license>', dependency.identifier, False)
            continue
        for lic in dependency.licenses:
            try:
                report.add_license(normalizer.match(lic),
                                   dependency.identifier,
                                   True)
            except complic.licenses.exceptions.UnknownLicenseError:
                report.add_license(lic, dependency.identifier, False)

    return report


def main(): # pragma: nocover
    desc = "Collect licensing information from package managers (mvn, npm, \
            pypi, etc.) and generate a complic-report.json with the results."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-v", "--verbose", action="store_true", \
        help="Increase output verbosity")
    parser.add_argument("-d", "--directory", default=os.getcwd(), \
        help="The directory to scan.")
    parser.add_argument("-n", "--name", default=None, \
        help="The name to identify this project with (defaults to directory).")

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s')
    logging.getLogger().setLevel(getattr(logging, 'INFO'))

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug('Verbose mode activated.')
    if not os.path.isdir(args.directory):
        logging.critical("Specified parameter directory doesn't look like one: %s", args.directory)
        sys.exit(1)

    if not args.name:
        args.name = args.directory

    report_path = os.path.join(args.directory, 'complic-report.json')
    report = engine(args.directory, args.name)

    logging.info("Writing complic report to: %s", report_path)
    with open(report_path, 'w') as report_file:
        report_file.write(json.dumps(report))

    logging.info(report.to_string())


if __name__ == '__main__': # pragma: nocover
    main()
