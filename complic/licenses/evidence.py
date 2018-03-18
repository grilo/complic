#!/usr/bin/env python

import logging
import json
import copy
import datetime


class Report(object):

    def __init__(self, name, compat_checkers=[]):
        self.name = name
        self.compat_checkers = compat_checkers
        self.licenses = {}
        self.dependencies = {}

    def add_compat(self, compat):
        self.compat_checkers.append(compat)

    def add_license(self, name, identifier, known):
        logging.debug("Report license: %s %s %s", name, identifier, known)
        if not name in self.licenses:
            self.licenses[name] = known
        if not identifier in self.dependencies:
            self.dependencies[identifier] = set()
        self.dependencies[identifier].add(name)

    def get_license_deps(self, lic):
        deps = set()
        for dep, licenses in self.dependencies.items():
            if lic in licenses:
                deps.add(dep)
        return deps

    @property
    def problems(self):
        problems = []

        for name, props in self.report_raw['compatibility'].items():
            if props['error']:

                deps = set()
                for lic in props['problems']:
                    deps = deps & self.get_license_deps(lic)

                problem = {
                    'licenses': props['problems'],
                    'dependencies': list(deps),
                    'description': props['description'],
                }

                problems.append(problem)

        for lic, known in self.licenses.items():
            if not known:
                deps = self.get_license_deps(lic)
                deps = ','.join(list(deps))
                desc = "Uknown/no license means no rights to use/modify/share."
                problem = {
                    'licenses': [lic],
                    'dependencies': list(self.get_license_deps(lic)),
                    'description': desc,
                }
                problems.append(problem)

        return problems

    @property
    def report_raw(self):

        report = {
            'date': datetime.datetime.now().strftime('%d %b %Y %H:%M'),
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


    def to_text(self):

        dep_count = len(self.dependencies)
        lic_count = len(self.licenses)

        probs = self.problems
        prob_count = len(probs)

        prob_list = []
        for p in self.problems:
            msg = "[{lic}] {reason}\n"
            msg += "\tDependencies: {deps}"
            prob_list.append(msg.format(lic=','.join(p['licenses']),
                                        reason=p['description'],
                                        deps=','.join(p['dependencies']))
                            )

        today = datetime.datetime.now().strftime('%d %b %Y %H:%M')
        msg = "On %s, a license analysis was performed," % (today)
        msg += " of project (%s), finding" % (self.name)
        msg += " %i unique dependencies," % (dep_count)
        msg += " %i licenses and" % (lic_count)
        msg += " %i problems." % (len(probs))
        if len(probs):
            msg += "\n\bProblems:\n"
            msg += ' - ' + '\n - '.join(prob_list)

        return msg

    def to_json(self):
        return json.dumps(self.report_raw)
