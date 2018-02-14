#!/usr/bin/env python

import logging

import utils.cache


class Registry(object):
    """Holds the approval state of each license."""

    def __init__(self):
        pass

    def is_approved(self, license):
        """
            If the given license is approved, return True.
            Otherwise, return False.
        """
        return False


class SPDX(object):
    """Given a string, finds the best SPDX match for it."""
