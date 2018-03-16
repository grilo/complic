#!/usr/bin/env python

"""
    Scans for license incompatibilities, GPL version.
"""

import logging


def get():
    return [GPL(), Forbidden()]


class Base(object):
    """Checks for incompatible liceneses.

        Expects a list of complic.scanner.base.Dependency objects.
    """

    def __init__(self, description):
        self.description = description
        self.original = set()
        self.incompatible = set()

    def check(self, licenses):
        """Given a list of licenses check for incompatibility."""

        result = {
            'description': self.description,
            'error': False,
            'problems': [],
        }

        if not isinstance(licenses, set):
            licenses = set(licenses)

        intersection = self.original & licenses
        if intersection:
            overlap = licenses & self.incompatible
            if overlap:
                logging.debug("Incompatible licenses found.")
                result['error'] = True
                result['problems'] = list(overlap)
                return result
        logging.debug("No incompatible licenses found.")
        return result


class GPL(Base):
    """Incompatibility with GPL licenses."""

    def __init__(self):
        desc = "Licenses incompatible with GPL licensed code."
        super(GPL, self).__init__(desc)

        self.original = set([
            'GPL-2.0',
            'GPL-3.0',
        ])
        self.incompatible = set([
            'AGPL-V1',
            'AFL-3.0',
            'Apache-1.1',
            'Apache-1.0',
            'APSL-2.0',
            'CDDL-1.0',
            'CPAL-1.0',
            'CPL-1.0',
            'Eclipse-1.0',
            'Eclipse-2.0',
            'EUPL-1.1',
            'IBMPL-1.0',
            'Lucent-1.02',
            'MS-PL',
            'Mozilla-1.1',
            'Nokia-1.0a',
            'OSL-3.0',
            'PHP-3.0',
            'SUNPublic-1.0',
        ])


class Forbidden(Base):
    """These licenses are completely forbidden from being used."""

    def __init__(self):
        desc = "Licenses forbidden from use."
        super(Forbidden, self).__init__(desc)
        self.original = set([
            'AGPL-V1',
        ])
        self.incompatible = self.original
