#!/usr/bin/env python

import os

from complic.utils import config


def test_no_key_raises_exception():
    m = config.Manager()
    try:
        m['hello']['blah'] = 'world'
        assert False
    except KeyError:
        assert True

def test_creates_dir(tmpdir):
    basedir = str(tmpdir.realpath())
    cfgfile = os.path.join(basedir, 'somefakedir', 'site.cfg')
    m = config.Manager(cfgfile)
    assert os.path.isdir(os.path.dirname(cfgfile))

def test_get_value(tmpdir):
    c = tmpdir.mkdir("config").join("site.cfg")
    c = str(c.realpath())
    fd = open(c, 'w')
    fd.write("[hello]\nworld=xpto")
    fd.close()
    m = config.Manager(c)
    assert m['hello']['world'] == 'xpto'

def test_set_value(tmpdir):
    c = tmpdir.mkdir("config").join("site.cfg")
    c = str(c.realpath())
    fd = open(c, 'w')
    fd.write("[hello]\nworld=xpto")
    fd.close()
    m = config.Manager(c)
    m['section'] = {
        'key': 'value'
    }
    assert m['section']['key'] == 'value'

def test_environment_overrides(tmpdir):
    os.environ['HELLO_WORLD'] = 'blah'
    c = tmpdir.mkdir("config").join("site.cfg")
    c = str(c.realpath())
    fd = open(c, 'w')
    fd.write("[hello]\nworld=xpto")
    fd.close()
    m = config.Manager(c)
    assert m['hello']['world'] == 'blah'

def test_iter_like_a_dict():
    m = config.Manager()
    m.options = {}
    m['hello'] = { 'world': 'one' }
    m['bye'] = { 'world': 'two' }
    for section in m:
        assert section in ['hello', 'bye']
