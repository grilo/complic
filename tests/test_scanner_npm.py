#!/usr/bin/env python

import distutils

from complic.scanner.npm import Scanner


def test_no_matches_if_not_in_path(mocker):
    mocker.patch.object(distutils.spawn, 'find_executable')
    distutils.spawn.find_executable.return_value = False

    mocker.patch.object(Scanner, 'handle_pkgjson')

    s = Scanner()
    s.scan([
        'hello/package.json',
        'world/anotherfile',
    ])
    Scanner.handle_pkgjson.no_calls()


def test_matches_pkgjson(mocker):
    mocker.patch.object(distutils.spawn, 'find_executable')
    distutils.spawn.find_executable.return_value = True

    mocker.patch.object(Scanner, 'handle_pkgjson')
    Scanner.handle_pkgjson.return_value = []
    s = Scanner()
    s.scan([
        'hello/package.json',
        'world/anotherfile',
    ])
    Scanner.handle_pkgjson.assert_called_once_with('hello/package.json')


def test_pkgjson_simple_license():
    pkgjson = {
        "name": "AFNetworking",
        "version": "3.2.0",
        "license": "MIT",
    }

    out = Scanner.get_licenses(pkgjson)
    assert len(out) == 1
    assert 'MIT' in out

def test_pkgjson_legacy_one():
    pkgjson = {
        "name": "AFNetworking",
        "version": "3.2.0",
        "license": [
            "LICENSE1",
            "LICENSE2"
        ]
    }

    out = Scanner.get_licenses(pkgjson)
    assert len(out) == 2
    assert 'LICENSE1' in out
    assert 'LICENSE2' in out

def test_podspec_weird_two_license():
    pkgjson = {
        "name": "AFNetworking",
        "version": "3.2.0",
        "licenses": [{
            "type": "LICENSE2",
            "file": "LICENSE"
        }]
    }
    out = Scanner.get_licenses(pkgjson)
    assert len(out) == 1
    assert 'LICENSE2' in out


def test_invalid_pkgjson(tmpdir):
    p = tmpdir.mkdir("project").join("package.json")
    p.write('bad json')
    pkgjson = str(p.realpath())
    out = Scanner.handle_pkgjson(pkgjson)
    assert not out

def test_valid_pkgjson(tmpdir):
    package_json = """{
        "name": "hello",
        "version": "1.0",
        "license": ["MIT", "GPLv2"]
    }"""
    p = tmpdir.mkdir("project").join("package.json")
    p.write(package_json)
    pkgjson = str(p.realpath())
    out = Scanner.handle_pkgjson(pkgjson)

    assert len(out) == 1
    assert out[0].identifier == 'js:hello:1.0'
    assert 'GPLv2' in out[0].licenses
    assert 'MIT' in out[0].licenses
