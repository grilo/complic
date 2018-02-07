#!/usr/bin/env python

import logging
import re
import decimal

import thirdparty.tfidf


class Matcher(object):

    @staticmethod
    def compare(corpus, string, threshold=0.005):
        results = corpus.similarities(string.split())

        # Remove exponential notation
        for r in results:
            if 'e' not in str(r[1]):
                continue
            idx = str(r[1]).index('e')
            r[1] = float(str(r[1])[:idx])

        # Discard results which are not similar enough
        results = [r for r in results if r[1] >= threshold]

        # Discard results which are too similar
        # Often small licenses contain very generic text
        # with multiple matches in the same license file
        # causing them to have huge scores.
        results = [r for r in results if r[1] <= 1.0]
        if not results:
            return '<unknown>'
        return sorted(results, key=lambda x: x[1])[-1][0]

    def __init__(self, registry):
        self.registry = registry

        # Build license corpus
        self.tfidf_license = thirdparty.tfidf.TfIdf()
        for k, v in self.registry.items():
            self.tfidf_license.add_document(k, v['licenseText'].split())

        # Build url corpus
        self.tfidf_url = thirdparty.tfidf.TfIdf()
        for k, v in self.registry.items():
            if 'seeAlso' not in v.keys():
                continue
            for url in v['seeAlso']:
                self.tfidf_url.add_document(k, url.split('/'))

        # Build name + spdx corpus (many projects use either)
        # Note, this may return really bad results
        self.tfidf_name = thirdparty.tfidf.TfIdf()
        for k, v in self.registry.items():
            self.tfidf_name.add_document(k, v['name'].split())
            self.tfidf_name.add_document(k, v['licenseId'].split())

    def text(self, string):
        return self.compare(self.tfidf_license, string)

    def url(self, string):
        return self.compare(self.tfidf_url, string)

    def name(self, string):
        return self.compare(self.tfidf_name, string)

    def best(self, string):
        """Scans all corpii and returns the best match."""
        results = []
        for corpus in [self.tfidf_name, self.tfidf_url, self.tfids_text]:
            results.append(self.compare(corpus, string))
        return sorted(results, key=lambda x: x[1])[-1][0]
