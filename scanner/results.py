#!/usr/bin/env python

import logging


class Aggregator(object):

    def __init__(self, filelist):
        self.filelist = filelist
        self.scanners = []

    def add_scanner(self, scanner):
        self.scanners.append(scanner)

    @property
    def report(self):
        all_results = {}
        merged_results = {}

        for s in self.scanners:
            for result in s.scan(self.filelist):
                if result is None:
                    continue
                if result.identifier not in all_results.keys():
                    all_results[result.identifier] = result
                else:
                    print result.path
                    for lic in result.licenses:
                        logging.info("Merging license (%s) onto: %s", lic, result.identifier)
                        all_results[result.identifier].licenses.add(lic)

        for path in all_results.keys():
            if not path.startswith('/'):
                merged_results[path] = all_results[path]
                continue

            for identifier, values in all_results.items():
                if path == identifier:
                    continue
                elif path == values.path:
                    merged_results[identifier] = values
                    for lic in all_results[path].licenses:
                        logging.info("Merging license (%s) onto: %s", lic, result.identifier)
                        merged_results[result.identifier].licenses.add(lic)

        return merged_results
