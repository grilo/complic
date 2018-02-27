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
import complic.scanner.java
import complic.scanner.npm
import complic.scanner.python
import complic.scanner.cocoapods
import complic.backend.exceptions
import complic.backend.artifactory


def get_scanners():
    """
        Scanners return a list of complic.scanner.base.Dependency objects
        which contain, among other things, the legal blurb we need.
    """
    return [
        #complic.scanner.java.Scanner(),
        #complic.scanner.npm.Scanner(),
        #complic.scanner.python.Scanner(),
        complic.scanner.cocoapods.Scanner(),
    ]

def get_meta(project_name, license_report):
    # Generate the following map:
    #   {
    #       'approved': 0,
    #       'not_approved': 0,
    #       'uknown': 0,
    #       'dependencies': 0,
    #       'evidence': 'On the 30th a scan was performed.',
    #   }
    meta = {
        'approved': 0,
        'not_approved': 0,
        'unknown': 0,
        'dependencies': 0,
        'evidence': '',
    }

    for name, values in license_report.items():
        if values['approved'] is None:
            meta['unknown'] += 1
        elif values['approved']:
            meta['approved'] += 1
        else:
            meta['not_approved'] += 1
        meta['dependencies'] += len(values['dependencies'])

    today = datetime.date.today().strftime('%d %b %Y')
    meta['evidence'] = "On %s, a license analysis was performed," % (today)
    meta['evidence'] += " of project (%s), finding" % (project_name)
    meta['evidence'] += " %i unique dependencies." % (meta['dependencies'])
    meta['evidence'] += " Detected %i licenses," % (len(license_report))
    meta['evidence'] += " having %i approved," % (meta['approved'])
    meta['evidence'] += " %i not approved and" % (meta['not_approved'])
    meta['evidence'] += " %i unknown." % (meta['unknown'])

    return meta


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

    # Matches strings to a SPDX
    spdx = complic.backend.artifactory.SPDX(config)

    # Contains the info whether a given SPDX is compliant or not
    registry = complic.backend.artifactory.Registry(config)

    # Generate the following map:
    # {
    #   '<license_spdx>': {
    #       'approved': True|False|None
    #       'dependencies': [ 'dependency1', 'dependency2' ]
    #   }

    license_report = {}
    for scanner in get_scanners():
        for dependency in scanner.scan(complic.utils.fs.Find(directory).files):
            for license_string in dependency.licenses:
                name = license_string
                approved = None
                try:
                    name = spdx.match(license_string)
                    approved = registry.is_approved(name)
                except complic.backend.exceptions.UnknownLicenseError:
                    pass

                if not name in license_report:
                    license_report[name] = {
                        'approved': approved,
                        'dependencies': [],
                    }
                if not dependency.identifier in license_report[name]['dependencies']:
                    license_report[name]['dependencies'].append(dependency.identifier)

    return license_report


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
    license_report = engine(args.directory)
    meta_report = get_meta(args.directory, license_report)

    logging.info("Writing complic report to: %s", report_path)
    with open(report_path, 'w') as report_file:
        report_file.write(json.dumps(license_report))

    logging.info(meta_report['evidence'])

    if meta_report['not_approved'] > 0:
        sys.exit(meta_report['not_approved'] + 1)


if __name__ == '__main__':
    main()
