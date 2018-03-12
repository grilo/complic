#!/usr/bin/env python

import logging


class Report(object):

    def __init__(self):
        pass

    def add_license(name, dependency):
        pass

    def add_unknown_license(self, name):
        pass

    def add_compat(self, name, result):
        pass

    def get_meta(self, project_name, license_report):
        # Generate the following map:
        #   {
        #       'uknown': 0,
        #       'dependencies': 0,
        #       'evidence': 'On the 30th a scan was performed.',
        #   }
        meta = {
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

