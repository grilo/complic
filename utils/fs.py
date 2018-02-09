#!/usr/bin/env python

import logging
import shutil
import tempfile
import os


class TemporaryDirectory(object):
    """Create and return a temporary directory.  This has the same
    behavior as mkdtemp but can be used as a context manager.  For
    example:
        with TemporaryDirectory() as tmpdir:
            ...
    Upon exiting the context, the directory and everything contained
    in it are removed.
    """

    def __init__(self, suffix='', prefix='tmp', dir=None):
        self.name = tempfile.mkdtemp(suffix, prefix, dir)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.name)

    def __enter__(self):
        return self.name

    def __exit__(self, exc, value, tb):
        logging.warning("Removing temporary directory: %s", self.name)
        shutil.rmtree(self.name)


class Find(object):

    def __init__(self, root):
        self.root = root
        self._files = []
        self._directories = []

        self._findall()

    def _findall(self):
        for root, dirs, files in os.walk(self.root):
            for f in files:
                self._files.append(os.path.join(root, f))
            for d in dirs:
                self._directories.append(os.path.join(root, d))

    @property
    def files(self):
        return self._files

    @property
    def dirs(self):
        return self._directories
