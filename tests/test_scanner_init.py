#!/usr/bin/env python

import re

import complic.scanner
from complic.scanner import base

def test_scanners_returned():
    assert len(complic.scanner.get()) > 0

def test_base_scanner():

    def handler(blah):
        return ['something']
    scanner = base.Scanner()
    scanner.register_handler(re.compile('.*'), handler)
    deps = scanner.scan(['some', 'file'])
    assert len(deps) == 2

