#!/usr/bin/env python

import os

from complic.utils import config


def test_no_key_raises_exception():
    m = config.Manager('fake_location')
    try:
        m['hello']['blah'] = 'world'
        assert False
    except KeyError:
        assert True

def test_invalid_config_format(tmpdir):
    c = tmpdir.mkdir("config").join("site.cfg")
    c = str(c.realpath())
    fd = open(c, 'w')
    fd.write('[ini]\nfile=format')
    fd.close()
    try:
        m = config.Manager(c)
        assert False
    except ValueError:
        assert True

def test_schema():
    m = config.Manager('fake_location')
    assert 'dependencies' in m.keys()
    assert 'forbidden' in m.keys()

def test_creates_dir(tmpdir):
    basedir = str(tmpdir.realpath())
    cfgfile = os.path.join(basedir, 'somefakedir', 'site.cfg')
    m = config.Manager(cfgfile)
    assert os.path.isdir(os.path.dirname(cfgfile))

def test_get_value(tmpdir):
    c = tmpdir.mkdir("config").join("site.cfg")
    c = str(c.realpath())
    fd = open(c, 'w')
    fd.write('{"hello": "world"}')
    fd.close()
    m = config.Manager(c)
    assert m['hello'] == 'world'

def test_set_saves_value(tmpdir):
    c = tmpdir.mkdir("config").join("site.cfg")
    c = str(c.realpath())
    fd = open(c, 'w')
    fd.write('{"hello": "world"}')
    fd.close()
    m = config.Manager(c)
    m['section'] = {
        'key': 'value'
    }

    x = config.Manager(c)
    assert m['section']['key'] == 'value'

def test_config_like_dict(tmpdir):
    c = tmpdir.mkdir("config").join("cfg")
    c = str(c.realpath())
    m = config.Manager(c)
    m.options = {}
    m['hello'] = { 'world': 'one' }
    m['bye'] = { 'world': 'two' }
    for section in m:
        assert section in ['hello', 'bye']
    for k, v in m.items():
        assert k in ['hello', 'bye']
