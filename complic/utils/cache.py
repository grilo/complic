#!/usr/bin/env python
"""
Cache mechanism.

Licensing information is usually not very lightweight, and repeated requests
put unnecessary strain on the network.
"""

import logging
import os
import time
import abc


class File(object):
    """Simple file-based cache mechanism.

    The contents are stored as plaintext in: ~/.complic/<name>/cache
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, name='default'):
        self.cache_dir = os.path.join(os.environ.get("HOME", os.getcwd()),
                                      '.complic',
                                      name)
        self.cache_ttl = 15811200  # Seconds
        self.contents = {}

    @abc.abstractmethod
    def refresh(self):
        """Requires implementation.

        Should contain the logic to be executed when the cache is marked as
        invalid. Should set "self.contents" to whatever was retrieved."""
        raise NotImplementedError

    def get(self):
        """Layered approach for handling the cache:
        1. prefer local disk.
        2. if not found or expired, download it
        """

        cache_file = os.path.join(self.cache_dir, 'cache')

        # If local cache is invalid, rebuild it
        if not os.path.isfile(cache_file) or \
            time.time() - os.path.getmtime(cache_file) > self.cache_ttl:
            logging.warning("Cache invalid, downloading...")

            if not os.path.isdir(self.cache_dir):
                os.makedirs(self.cache_dir)

            lock = os.path.join(self.cache_dir, '.updating')
            if os.path.isfile(lock):
                return self.contents
            open(lock, 'w').close()
            try:
                self.contents = self.refresh()
            finally:
                os.remove(lock)

            with open(cache_file, 'w') as cache_fd:
                logging.info("Caching results...")
                cache_fd.write(self.contents)

        # Return locally stored contents
        if not self.contents:
            logging.debug("Retrieving cached content...")
            try:
                self.contents = open(cache_file, 'r').read()
            except IOError:
                logging.critical("Unable to read cache from disk.")
                logging.critical("Intervention required: %s", self.cache_dir)

        return self.contents
