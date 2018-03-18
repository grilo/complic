#!/usr/bin/env python
"""
Filesystem handling utilities.
"""

import logging
import shutil
import tempfile
import os


class Find(object):
    """Traverse the filesystem and build file and directory lists.

    Everything inside .git is ignored by default."""

    def __init__(self, root):
        self.root = root
        self._files = []
        self._directories = []

        self._findall()

    def _findall(self):
        """Store the results in object attributes, ignore .git files."""
        logging.debug("Retrieving file list from: %s", self.root)
        for root, dirs, files in os.walk(self.root):
            if r'/.git' in root: # pragma: nocover
                continue
            for filename in files:
                self._files.append(os.path.join(root, filename))

    @property
    def files(self):
        return self._files


class chdir(object):

    def __init__(self, new_dir):
        self.old_dir = os.getcwd()
        self.new_dir = new_dir

    def __enter__(self):
        logging.debug("Changing directory to: %s", self.new_dir)
        os.chdir(self.new_dir)
        return self.new_dir

    def __exit__(self, *args):
        logging.debug("Changing directory to: %s", self.old_dir)
        os.chdir(self.old_dir)
        return self.old_dir
