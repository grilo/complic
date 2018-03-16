#!/usr/bin/env python


import json


import pytest

from complic.licenses import evidence
from complic.licenses import compat


@pytest.fixture
def report(mocker):
    mocker.patch.object(compat, 'Base')
    compat.Base.return_value.check.return_value = {
        'error': True,
        'description': 'important description',
        'problems': 'Found one!',
    }

    rep = evidence.Report('report name')
    rep.add_compat(compat.Base())
    rep.add_license('lic_name', 'some:identifier', True)
    rep.add_license('another_lic', 'some:identifier', False)

    return rep


def test_report(report):

    out = report.report_raw
    assert out['licenses']['lic_name'] == True
    assert out['licenses']['another_lic'] == False
    assert len(out['dependencies'].keys()) == 1
    assert out['dependencies']['some:identifier']
    assert out['compatibility']['MagicMock']['problems'] == 'Found one!'

def test_report_json(report):
    json.loads(report.to_json())

def test_report_text(report):
    assert isinstance(report.to_text(), str)
