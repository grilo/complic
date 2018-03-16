#!/usr/bin/env python

import logging
import json
import copy
import datetime


class Report(object):

    def __init__(self, name):
        self.name = name
        self.compat_checkers = []
        self.licenses = {}
        self.dependencies = {}

    def add_compat(self, compat):
        self.compat_checkers.append(compat)

    def add_license(self, name, identifier, known):
        if not name in self.licenses:
            self.licenses[name] = known
        if not identifier in self.dependencies:
            self.dependencies[identifier] = set()
        self.dependencies[identifier].add(name)

    @property
    def report_raw(self):

        report = {
            'licenses': copy.deepcopy(self.licenses),
            'dependencies': {},
            'compatibility': {},
        }

        for dep, licenses in self.dependencies.items():
            report['dependencies'][dep] = list(licenses)

        lics = self.licenses.keys()
        for checker in self.compat_checkers:
            name = checker.__class__.__name__
            report['compatibility'][name] = checker.check(lics)

        return report

    @property
    def stats(self):
        dep_count = len(self.dependencies)
        lic_count = len(self.licenses)
        prob_count = 0
        for name, props in self.report_raw['compatibility'].items():
            if props['error']:
                prob_count += len(props['problems'])

        return {
            'dependencies': dep_count,
            'licenses': lic_count,
            'problems': prob_count,
        }

    def to_json(self):
        return json.dumps(self.report_raw)

    def to_text(self):

        stats = self.stats

        today = datetime.date.today().strftime('%d %b %Y')
        msg = "On %s, a license analysis was performed," % (today)
        msg += " of project (%s), finding" % (self.name)
        msg += " %i unique dependencies and" % (stats['dependencies'])
        msg += " %i licenses, and" % (stats['licenses'])
        msg += " %i problems." % (stats['problems'])

        return msg
