#!/usr/bin/env python

import logging
import os

import legal.registry
import legal.text
import scanner.javascript
import scanner.results


def list_files(directory):
    for root, dirs, files in os.walk(directory):
        for f in files:
            yield os.path.join(root, f)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s')
    logging.getLogger().setLevel(getattr(logging, 'INFO'))

    logging.getLogger().setLevel(logging.DEBUG)

    directory = '/home/grilo/projects/sourcejenkins/electron-quick-start/node_modules'

    matcher = legal.text.Matcher(legal.registry.licenses)

    aggregator = scanner.results.Aggregator(list_files(directory))
    aggregator.add_scanner(scanner.javascript.Scanner(matcher))

    import pprint
    pprint.pprint(aggregator.report)

    #s = scanner.javascript.Scanner(matcher)
    #for r in s.scan(list_files(directory)):
    #    if r is None:
    #        continue
    #
    #    print "Found match (%s), with lics: %s" % (r.identifier, r.licenses)
