#!/usr/bin/env python

import pytest

from complic.licenses import compat


original_lics = ['hello', 'world']
incompat_lics = ['blah']


def test_has_compatible_licenses_with_orig():
    c = compat.Base()
    c.original = set(original_lics)
    c.incompatible = set(incompat_lics)
    assert c.check(['world']) == True

def test_has_compatible_licenses_with_random():
    c = compat.Base()
    c.original = set(original_lics)
    c.incompatible = set(incompat_lics)
    assert c.check(['xpto']) == True

def test_no_incompatible_licenses():
    c = compat.Base()
    c.original = set(original_lics)
    c.incompatible = set(incompat_lics)
    assert c.check(['hello', 'blah']) == False

def test_incompatible_gpl():
    c = compat.GPL()
    assert c.check(['GPL-2.0', 'CDDL-1.0']) == False

def test_compatible_gpl():
    c = compat.GPL()
    assert c.check(['GPL-2.0', 'Mozilla-2.0']) == True

def test_forbidden_bad_license():
    c = compat.Forbidden()
    assert c.check(['AGPL-V1']) == False

def test_forbidden_good_license():
    c = compat.Forbidden()
    assert c.check(['GPL-V3']) == True
