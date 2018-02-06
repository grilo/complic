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
        results = {}
        for s in self.scanners:
            for result in s.scan(self.filelist):

                # Merge results
                if result.path in results:
                    p = result.path
                    result = results[p].merge(result)
                    # Don't keep paths if we can avoid it
                    del results[p]
                elif result.identifier in results:
                    result = results[result.identifier].merge(result)

                results[result.identifier] = result

        return results
