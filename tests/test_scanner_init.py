#!/usr/bin/env python

import complic.scanner

def test_scanners_returned():
    assert len(complic.scanner.get()) > 0
