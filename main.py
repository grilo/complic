#!/usr/bin/env python

import logging
import os

import legal.registry
import legal.tfidf
import utils.fs
import scanner.java
import scanner.js
import scanner.python


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s')
    logging.getLogger().setLevel(getattr(logging, 'INFO'))

    logging.getLogger().setLevel(logging.DEBUG)

    #directory = '/home/grilo/projects/sourcejenkins/electron-quick-start/node_modules'
    #directory = '/home/grilo/projects/sourcejenkins/hola'
    #directory = '/home/grilo/projects/sourcejenkins/jenkins'
    #directory = '/home/grilo/projects/sourcejenkins/python/pipreqs'
    directory = '/home/grilo/projects/sourcejenkins/python/huxley'


    matcher = legal.tfidf.Matcher(legal.registry.SPDX().licenses)

    scanners = [
        #scanner.java.Scanner(matcher),
        #scanner.js.Scanner(matcher),
        scanner.python.Scanner(matcher),
    ]

    report = {}

    for scanner in scanners:
        for dependency in scanner.scan(utils.fs.Find(directory).files):

            if dependency.identifier in report:
                # Merge the old dependency with the new one
                new_dep = report[dependency.identifier].merge(dependency)
                del report[dependency.identifier]
                dependency = new_dep

            report[dependency.identifier] = dependency

    for k, v in report.items():
        print v.scanner, k, ','.join(v.licenses)
