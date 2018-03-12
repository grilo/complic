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
import complic.utils.config

import complic.scanner

import complic.licenses.exceptions
import complic.licenses.regex
import complic.licenses.compat
import complic.licenses.evidence


def get_dependencies(scanners, files):
    dependencies = []
    for dependency in scanner.scan(files):
        dependencies.append(dependency)
    return dependencies


def get_licenses(normalizer, dependencies):
    unknown = set()
    licenses = {}
    for dependency in dependencies:
        for lic_string in dependency.licenses:
            try:
                spdx = normalizer.match(lic_string)
            except complic.licenses.exceptions.UnknownLicenseError:
                unknown.add(lic_string)
                spdx = lic_string

            if not spdx in licenses:
                licenses[spdx] = set()
            licenses[spdx].add(dependency.identifier)
    return licenses, unknown


def engine(directory):
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

    config = complic.utils.config.Manager()

    # Normalizes strings into the SPDX index (when possible)
    normalizer = complic.licenses.regex.Normalizer()

    # Generate the following map:
    # {
    #   '<license_spdx>': {
    #       'approved': True|False|None
    #       'dependencies': [ 'dependency1', 'dependency2' ]
    #   }

    filelist = complic.utils.fs.Find(directory).files
    report = complic.licenses.evidence.Report()


    dependencies = get_dependencies(complic.scanner.get(), filelist)

    license_dependencies, unknown = get_licenses(dependencies)

    for lic, deps in license_dependencies.items():
        report.add_license(lic, deps)
        if lic in unknown:
            report.add_unknown_license(lic)

    for compat_checker in complic.licenses.compat.get():
        name = compat_checker.__class__.__name__
        result = compat_checker.check(license_dependencies.keys())
        report.add_compat(name, result)

    return report


def main():
    desc = "Collect licensing information from package managers (mvn, npm, \
            pypi, etc.) and generate a complic-report.json with the results."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-v", "--verbose", action="store_true", \
        help="Increase output verbosity")
    parser.add_argument("-d", "--directory", default=os.getcwd(), \
        help="The directory to scan.")

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s')
    logging.getLogger().setLevel(getattr(logging, 'INFO'))

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug('Verbose mode activated.')
    if not os.path.isdir(args.directory):
        logging.critical("Specified parameter directory doesn't look like one: %s", args.directory)
        sys.exit(1)

    report_path = os.path.join(args.directory, 'complic-report.json')
    report = engine(args.directory)

    logging.info("Writing complic report to: %s", report_path)
    with open(report_path, 'w') as report_file:
        report_file.write(json.dumps(report))

    logging.info(report.to_string())


if __name__ == '__main__':
    main()
