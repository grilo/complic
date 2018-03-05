#!/usr/bin/env python

"""
    Scans for license incompatibilities.
"""


class Base(object):
    """Checks for incompatible liceneses.

        Expects a list of complic.scanner.base.Dependency objects.
    """

    def __init__(self):
        self.original = set()
        self.incompatible = set()

    def check(self, licenses):
        """Given a list of licenses check for incompatibility."""

        gpl = self.original & licenses
        if gpl:
            if licenses & self.incompatible:
                return False
        return True


class GPL(Base):
    """Setup incompatibility for GPL licenses."""

    def __init__(self):
        super(GPL, self).__init__()

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
