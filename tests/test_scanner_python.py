#!/usr/bin/env python

import distutils
import os

from complic.utils import shell
from complic.utils import fs
from complic.scanner.python import Scanner


def test_no_matches_if_not_in_path(mocker):
    mocker.patch.object(distutils.spawn, 'find_executable')
    distutils.spawn.find_executable.return_value = False

    mocker.patch.object(Scanner, 'handle_setuppy')

    s = Scanner()
    s.scan([
        'hello/setup.py',
        'world/anotherfile',
    ])
    Scanner.handle_setuppy.no_calls()


def test_matches_pkgjson(mocker):
    mocker.patch.object(distutils.spawn, 'find_executable')
    distutils.spawn.find_executable.return_value = True

    mocker.patch.object(Scanner, 'handle_setuppy')
    Scanner.handle_setuppy.return_value = []
    s = Scanner()
    s.scan([
        'hello/setup.py',
        'world/anotherfile',
    ])
    Scanner.handle_setuppy.assert_called_once_with('hello/setup.py')

def test_parse_metadata():

    metadata = """Metadata-Version: 1.1
    Name: gateone
    Version: 1.2.0
    License: AGPLv3 or Proprietary
    Description-Content-Type: UNKNOWN
    Description: Gate One is a web-based terminal emulator and SSH client that requires no browser plugins and includes many unique and advanced features.
    Classifier: License :: OSI Approved :: GNU Affero General Public License v3
    Classifier: License :: Other/Proprietary License
    """

    identifier, lic = Scanner.parse_metadata(metadata)
    assert identifier == 'python:gateone:1.2.0'
    assert lic == 'AGPLv3 or Proprietary'


def test_with_extra_requirements(tmpdir):
    p = tmpdir.mkdir("project").join("setup.py")
    setuppy = """import setuptools
something = {'hello': 'world'}
setuptools.setup(extras_require=something)
"""
    p.write(setuppy)
    setuppy = str(p.realpath())
    out = Scanner.get_extra_requirements(setuppy)
    print out
    assert len(out) == 1
    assert 'hello' in out

def test_without_extra_requirements(tmpdir):
    p = tmpdir.mkdir("project").join("setup.py")
    setuppy = """import setuptools
setuptools.setup()
"""
    p.write(setuppy)
    setuppy = str(p.realpath())
    out = Scanner.get_extra_requirements(setuppy)
    assert not out

def test_pip_install_ok(tmpdir, mocker):
    mocker.patch.object(shell, 'cmd')
    shell.cmd.return_value = (0, '', '')
    p = tmpdir.mkdir("project").join("setup.py")
    setuppy = str(p.realpath())

    expected = "PYTHONUSERBASE='%s' " % (os.path.dirname(setuppy))
    expected += "pip install --ignore-installed .[an_extra]"
    assert Scanner.pip_install(setuppy, ['an_extra']) == True
    assert shell.cmd.called_once_with(expected)

def test_pip_install_error(tmpdir, mocker):
    mocker.patch.object(shell, 'cmd')
    shell.cmd.return_value = (1, '', '')
    p = tmpdir.mkdir("project").join("setup.py")
    setuppy = str(p.realpath())

    assert Scanner.pip_install(setuppy) == False


def test_handle_setuppy_happy_path(tmpdir, mocker):

    mocker.patch.object(Scanner, 'get_extra_requirements')
    Scanner.get_extra_requirements.return_value = 'a_requirement'

    mocker.patch.object(Scanner, 'pip_install')
    Scanner.pip_install.return_value = True

    #mocker.patch.object(fs, 'Find')
    #fs.Find.return_value.files = ['/something/bad', '/a/PKG-INFO', '/b/METADATA']

    somedir = tmpdir.mkdir("project")
    random_file = somedir.join("randomfile")
    random_file.write('aaaa')
    pkg_info = somedir.join("PKG-INFO")
    pkg_info.write("Name: xxx\nVersion: 2.0.1\nLicense: GPLv2\n")
    metadata = somedir.join("METADATA")
    metadata.write("Name: aaa\nVersion: 1.0.0\nLicense: Unlicense\n")
    setuppy = somedir.join("setup.py")
    setuppy = str(setuppy.realpath())

    deps = Scanner.handle_setuppy(setuppy)

    assert len(deps) == 2
    for d in deps:
        assert d.identifier in ['python:xxx:2.0.1', 'python:aaa:1.0.0']
        assert list(d.licenses)[0] in ['GPLv2', 'Unlicense']

def test_handle_setuppy_error_pipinstall(tmpdir, mocker):

    mocker.patch.object(Scanner, 'get_extra_requirements')
    Scanner.get_extra_requirements.return_value = 'a_requirement'

    mocker.patch.object(Scanner, 'pip_install')
    Scanner.pip_install.return_value = False

    assert not Scanner.handle_setuppy('fake')
