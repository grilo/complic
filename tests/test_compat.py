#!/usr/bin/env python

import pytest

from complic.licenses import compat


original_lics = ['hello', 'world']
incompat_lics = ['blah']


def test_compatible_with_orig():
    desc = "important description"
    c = compat.Base(desc)
    c.original = set(original_lics)
    c.incompatible = set(incompat_lics)
    out = c.check(['world'])
    assert out['description'] == "important description"
    assert out['error'] == False
    assert not out['problems']

def test_compatible_with_random():
    desc = "important description"
    c = compat.Base(desc)
    c.original = set(original_lics)
    c.incompatible = set(incompat_lics)
    out = c.check(['xpto'])
    assert out['description'] == "important description"
    assert out['error'] == False
    assert not out['problems']

def test_incompatible():
    desc = "important description"
    c = compat.Base(desc)
    c.original = set(original_lics)
    c.incompatible = set(incompat_lics)
    out = c.check(['hello', 'blah'])
    assert out['description'] == "important description"
    assert out['error'] == True
    assert len(out['problems']) == 1
    assert 'blah' in out['problems']

def test_incompatible_gpl():
    c = compat.GPL()
    lics = ['GPL-2.0', 'CDDL-1.0']
    out = c.check(lics)
    assert out['error'] == True
    assert len(out['problems']) == 1
    assert 'CDDL-1.0' in out['problems']


def test_compatible_gpl():
    c = compat.GPL()
    lics = ['GPL-2.0', 'Mozilla-2.0']
    out = c.check(lics)
    assert out['error'] == False
    assert not out['problems']

def test_forbidden_bad_license():
    c = compat.Forbidden()
    lics = ['AGPL-V1']
    out = c.check(lics)
    assert out['error'] == True
    assert len(out['problems']) == 1
    assert 'AGPL-V1' in out['problems']

def test_forbidden_good_license():
    c = compat.Forbidden()
    lics = ['GPL-V3']
    out = c.check(lics)
    assert out['error'] == False
    assert not out['problems']

def test_returns_compat_engines():
    for engine in compat.get():
        assert hasattr(engine, 'check')
