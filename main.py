#!/usr/bin/env python

import logging
import os

import legal.registry
import legal.text
import utils.fs
import scanner.js
import scanner.java
import scanner.results


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s')
    logging.getLogger().setLevel(getattr(logging, 'INFO'))

    logging.getLogger().setLevel(logging.INFO)

    #directory = '/home/grilo/projects/sourcejenkins/electron-quick-start/node_modules'
    directory = '/home/grilo/projects/sourcejenkins/hola'

    matcher = legal.text.Matcher(legal.registry.SPDX().licenses)

    aggregator = scanner.results.Aggregator(utils.fs.Find(directory).files)
    #aggregator.add_scanner(scanner.js.Scanner(matcher))
    aggregator.add_scanner(scanner.java.Scanner(matcher))

    #import pprint
    #pprint.pprint(aggregator.report)
    for k, v in aggregator.report.items():
        print k, v, v.path
