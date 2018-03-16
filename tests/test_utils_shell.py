#!/usr/bin/env python

from complic.utils import shell

def test_command_ok():
    rc, out, err = shell.cmd(u'ls')
    assert rc == 0
    assert not err
    assert out

def test_command_nok():
    rc, out, err = shell.cmd('ls doesntexist')
    assert rc != 0
    assert not out
    assert err
