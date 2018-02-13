#!/usr/bin/env python

import logging
import argparse
import os

import utils.fs
import scanner.java
import scanner.js
import scanner.python

import legal.artifactory


if __name__ == '__main__':


    desc = "Collects all licensing information reported by several package managers (mvn, npm, pypi, etc.)."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-v', '--verbose', action='store_true', \
        help='Increase output verbosity')
    parser.add_argument('-d', '--directory', default=os.getcwd(), \
        help='The directory to scan.')
    parser.add_argument('-f', '--format', default='pretty', \
        help='The output format (csv, json or pretty).')

    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s')
    logging.getLogger().setLevel(getattr(logging, 'INFO'))

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug('Verbose mode activated.')
    if not os.path.isdir(args.directory):
        logging.critical("Specified parameter directory doesn't look like one: %s", args.directory)
        sys.exit(1)


    matcher = legal.artifactory.Matcher(legal.artifactory.Cache().licenses)

    scanners = [
        scanner.java.Scanner(matcher),
        scanner.js.Scanner(matcher),
        scanner.python.Scanner(matcher),
    ]

    report = {}

    for scanner in scanners:
        for dependency in scanner.scan(utils.fs.Find(args.directory).files):

            if dependency.identifier in report:
                # Merge the old dependency with the new one
                new_dep = report[dependency.identifier].merge(dependency)
                del report[dependency.identifier]
                dependency = new_dep

            report[dependency.identifier] = dependency

    if args.format == 'pretty':
        for name, dep in report.items():
            print name, ','.join(dep.licenses)
    elif args.format == 'csv':
        items = []
        for name, dep in report.items():
            items.append(name)
            items.append(' '.join(dep.licenses))
        print ','.join(items)
    elif args.format == 'json':
        items = {}
        for name, dep in report.items():
            items[name] = list(dep.licenses)
        import jsono
        print json.dumps(items)
