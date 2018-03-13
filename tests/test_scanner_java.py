#!/usr/bin/env python

import distutils

from complic.scanner.java import Scanner
from complic.utils import shell
from complic.utils import fs


def test_no_matches_if_not_in_path(mocker):
    mocker.patch.object(distutils.spawn, 'find_executable')
    distutils.spawn.find_executable.return_value = False

    mocker.patch.object(Scanner, 'handle_pom')

    s = Scanner()
    s.scan([
        'hello/pom.xml',
        'world/anotherfile',
    ])
    Scanner.handle_pom.no_calls()


def test_matches_pomfiles(mocker):
    mocker.patch.object(distutils.spawn, 'find_executable')
    distutils.spawn.find_executable.return_value = True

    mocker.patch.object(Scanner, 'handle_pom')
    Scanner.handle_pom.return_value = []
    s = Scanner()
    s.scan([
        'hello/pom.xml',
        'world/anotherfile',
    ])
    Scanner.handle_pom.assert_called_once_with('hello/pom.xml')

def test_parse_thirdparty():
    thirdparty = """Lists of 11 third-party dependencies.
     (Unknown license) antlr (antlr:antlr:2.7.2 - no url defined)
     (Unknown license) commons-beanutils (commons:beanutils:1.7.0 - no url defined)
     (GPLv2) Commons Chain (commons:chain:1.1 - http://jakarta/${pom.artifactId.substring(8)}/)
     (MIT) Commons Chain (commons:chain:1.1 - http://jakarta/${pom.artifactId.substring(8)}/)
     (Common Public License Version 1.0) JUnit (junit:junit:3.8.1 - http://junit.org)
    """

    out = Scanner.parse_thirdparty(thirdparty)
    assert len(out) == 4
    assert 'java:antlr:antlr:2.7.2' in out
    assert 'java:commons:beanutils:1.7.0' in out
    assert 'java:commons:chain:1.1' in out
    assert 'java:junit:junit:3.8.1' in out
    assert 'Unknown license' in out['java:antlr:antlr:2.7.2']
    assert 'GPLv2' in out['java:commons:chain:1.1']
    assert 'MIT' in out['java:commons:chain:1.1']


def test_handle_bad_pom(mocker):
    mocker.patch.object(shell, 'cmd')
    shell.cmd.return_value = (1, '', '')
    assert not Scanner.handle_pom('fake_path')

def test_handle_good_pom(tmpdir, mocker):

    mocker.patch.object(shell, 'cmd')
    shell.cmd.return_value = (0, '', '')

    p = tmpdir.mkdir("project").join("THIRD-PARTY.txt")
    p.write('fake')
    thirdparty_txt = str(p.realpath())

    mocker.patch.object(fs, 'Find')
    fs.Find.return_value.files = ['/absolute/path', thirdparty_txt]

    mocker.patch.object(Scanner, 'parse_thirdparty')
    Scanner.parse_thirdparty.return_value = {
        'java:commons:chain:1.1': set(['GPLv2', 'MIT']),
        'java:antlr:antlr:2.7.2': set(['Uknown license']),
    }

    dependencies = Scanner.handle_pom('fake')

    assert len(dependencies) == 2
    assert dependencies[0].identifier == 'java:antlr:antlr:2.7.2'
    assert dependencies[1].identifier == 'java:commons:chain:1.1'
    assert len(dependencies[0].licenses) == 1
    assert len(dependencies[1].licenses) == 2
