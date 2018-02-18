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
            if r'/.git' in root:
                continue
            for filename in files:
                self._files.append(os.path.join(root, filename))
            for dirname in dirs:
                self._directories.append(os.path.join(root, dirname))

    @property
    def files(self):
        return self._files

    @property
    def dirs(self):
        return self._directories
