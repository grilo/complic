#!/usr/bin/env python

import pytest

from complic.licenses import regex
from complic.licenses import exceptions


lics = {
    'some_license': {
        'regexp': 'aaa .*'
    }

}

def test_normalizer_loads_default_licenses():
    n = regex.Normalizer()
    assert len(n.licenses.keys()) > 0

def test_normalizer_no_key_match():
    n = regex.Normalizer(lics)
    with pytest.raises(exceptions.UnknownLicenseError):
        n.match('some_random_string')

def test_normalizer_no_regex_match():
    n = regex.Normalizer(lics)
    with pytest.raises(exceptions.UnknownLicenseError):
        n.match('aaab')

def test_normalizer_match():
    n = regex.Normalizer(lics)
    assert n.match('aaa hello world') == 'some_license'

