#!/usr/bin/env python

import distutils

import pytest

import complic.scanner.cocoapods

podfile = """PODS:
  - AFNetworking (2.6.3):
    - AFNetworking/NSURLConnection (= 2.6.3)
    - AFNetworking/NSURLSession (= 2.6.3)
  - AFNetworking/NSURLConnection (2.6.3):
    - AFNetworking/Reachability
  - PureLayout (3.0.2)

DEPENDENCIES:
  - AFNetworking (~> 2.6.0)
  - BraintreeDropIn (from `BraintreeDropIn.podspec`)

EXTERNAL SOURCES:
  BraintreeDropIn:
    :podspec: BraintreeDropIn.podspec

EXTERNAL SOURCES:
  BraintreeDropIn:
    :podspec: BraintreeDropIn.podspec

CHECKOUT OPTIONS:
  BraintreeDropIn:
    :commit: 87e2254148bed745d246e2ac7866b22c3c5fabc2
    :git: https://github.com/braintree/braintree-ios-drop-in.git

SPEC CHECKSUMS:
  AFNetworking: cb8d14a848e831097108418f5d49217339d4eb60

PODFILE CHECKSUM: 4a4706f8c5de8995930f5c2ca08c0bcfb13740e1

COCOAPODS: 1.4.0"""


def test_no_matches_if_not_in_path(mocker):
    mocker.patch.object(distutils.spawn, 'find_executable')
    distutils.spawn.find_executable.return_value = False

    mocker.patch.object(complic.scanner.cocoapods.Scanner, 'handle_podfile')
    complic.scanner.cocoapods.Scanner.handle_podfile.return_value = []
    s = complic.scanner.cocoapods.Scanner()
    s.scan([
        'hello/Podfile.lock',
        'world/anotherfile',
    ])
    assert complic.scanner.cocoapods.Scanner.handle_podfile.assert_called_once_with('hello/Podfile.lock') == False


def test_matches_podfiles(mocker):
    mocker.patch.object(distutils.spawn, 'find_executable')
    distutils.spawn.find_executable.return_value = True

    mocker.patch.object(complic.scanner.cocoapods.Scanner, 'handle_podfile')
    complic.scanner.cocoapods.Scanner.handle_podfile.return_value = []
    s = complic.scanner.cocoapods.Scanner()
    s.scan([
        'hello/Podfile.lock',
        'world/anotherfile',
    ])
    complic.scanner.cocoapods.Scanner.handle_podfile.assert_called_once_with('hello/Podfile.lock')


def test_handle_podfile(tmpdir):
    p = tmpdir.mkdir("project").join("Podfile.lock")
    p.write(podfile)

    path = str(p.realpath())

    assert len(complic.scanner.cocoapods.Scanner.handle_podfile(path)) > 0



"""
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

"""
