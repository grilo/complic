#!/usr/bin/env python

from complic.utils import fs

from complic import cli
from complic.utils import config
from complic.licenses import evidence


def test_get_dependencies(mocker):
    scanner_a = mocker.Mock()
    scanner_a.scan.return_value = ['dependency1']

    scanner_b = mocker.Mock()
    scanner_b.scan.return_value = ['dependency2']

    out = cli.get_dependencies([scanner_a, scanner_b], ['list', 'of', 'files'])

    assert len(out) == 2
    assert 'dependency1' in out
    assert 'dependency2' in out


def test_engine(mocker):
    mocker.patch.object(fs, 'Find')
    mocker.patch.object(cli, 'get_dependencies')
    mocker.patch.object(config, 'Manager')
    config.Manager.return_value = {
        'dependencies': {
            'npm:package:1.1.1': 'GPL-V2'
        }
    }


    dep1 = mocker.Mock()
    dep1.identifier = 'python:package:1.0rc-3'
    dep1.licenses = set(['GPL-V3'])

    dep2 = mocker.Mock()
    dep2.identifier = 'java:some.group:artifact_id:5.2'
    dep2.licenses = set(['unknown', 'AGPL-V1'])

    dep3 = mocker.Mock()
    dep3.identifier = 'npm:forbidden:1.0.0'
    dep3.licenses = set(['AGPL-V1'])

    dep4 = mocker.Mock()
    dep4.identifier = 'npm:package:1.1.1'
    dep4.licenses = set([])

    dep5 = mocker.Mock()
    dep5.identifier = 'npm:package:2.1.1'
    dep5.licenses = set([])

    cli.get_dependencies.return_value = [
        dep1, dep2, dep3, dep4, dep5
    ]

    report = cli.engine('/some/dir', 'project_name')
    # Shouldn't really be testing types, but I don't know
    # what else to put here.
    assert isinstance(report, evidence.Report)
