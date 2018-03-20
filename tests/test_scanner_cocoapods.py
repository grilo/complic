#!/usr/bin/env python

import distutils

from complic.scanner.cocoapods import Scanner
from complic.utils import shell


def test_no_matches_if_not_in_path(mocker):
    mocker.patch.object(distutils.spawn, 'find_executable')
    distutils.spawn.find_executable.return_value = False

    mocker.patch.object(Scanner, 'handle_podfile')

    s = Scanner()
    s.scan([
        'hello/Podfile.lock',
        'world/anotherfile',
    ])
    Scanner.handle_podfile.no_calls()


def test_matches_podfiles(mocker):
    mocker.patch.object(distutils.spawn, 'find_executable')
    distutils.spawn.find_executable.return_value = True

    mocker.patch.object(Scanner, 'handle_podfile')
    Scanner.handle_podfile.return_value = []
    s = Scanner()
    s.scan([
        'hello/Podfile.lock',
        'world/anotherfile',
    ])
    Scanner.handle_podfile.assert_called_once_with('hello/Podfile.lock')

def test_bad_podspec_empty_dict(mocker):
    mocker.patch.object(shell, 'cmd')
    shell.cmd.return_value = (1, 'Unable to find a pod with name matching', '')
    out = Scanner.get_podspec('AFNetworking')
    assert not out
    assert isinstance(out, dict)

def test_good_podspec_returns_json(mocker):
    mocker.patch.object(shell, 'cmd')
    shell.cmd.return_value = (0, '{"hello": "world"}', '')
    out = Scanner.get_podspec('AFNetworking')
    assert len(out) == 1
    assert out["hello"] == "world"

def test_ids_from_podfile():
    podfile = """PODS:
      - AFNetworking (2.6.3):
        - AFNetworking/NSURLConnection (= 2.6.3)
        - AFNetworking/NSURLSession (= 2.6.3)

    DEPENDENCIES:
      - AFNetworking (~> 2.6.0)
      - BraintreeDropIn (from `BraintreeDropIn.podspec`)

    EXTERNAL SOURCES:
      BraintreeDropIn:
        :podspec: BraintreeDropIn.podspec
    COCOAPODS: 1.4.0"""

    ids = Scanner.get_ids_from_podfile(podfile)
    assert len(ids) == 2
    assert 'pod:AFNetworking:2.6.3' in ids
    assert 'pod:AFNetworking:2.6.0' in ids

def test_handle_podfile(tmpdir, mocker):
    mocker.patch.object(Scanner, 'get_ids_from_podfile')
    Scanner.get_ids_from_podfile.return_value = [
        'pod:AFNetworking:2.6.3',
    ]

    mocker.patch.object(Scanner, 'get_podspec')
    Scanner.get_podspec.return_value = {
        "name": "AFNetworking",
        "version": "3.2.0",
        "license": "MIT",
    }

    p = tmpdir.mkdir("project").join("Podfile.lock")
    p.write('fake')
    path = str(p.realpath())

    dependencies = Scanner.handle_podfile(path)
    assert len(dependencies) == 1
    assert dependencies[0].identifier == 'pod:AFNetworking:2.6.3'
    assert len(dependencies[0].licenses) == 1
    assert 'MIT' in dependencies[0].licenses
