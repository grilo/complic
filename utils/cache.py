#!/usr/bin/env python

import logging
import os
import time
import multiprocessing as mp


class File(object):

    def __init__(self, name='default'):
        self.cache_dir = os.path.join(os.environ.get("HOME", os.getcwd()), '.complic', name)
        self.cache_ttl = 15811200  # Seconds
        self.contents = {}

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

            with open(cache_file, 'w') as fd:
                logging.info("Caching results...")
                fd.write(self.contents)

        # Return locally stored contents
        if not self.contents:
            logging.debug("Retrieving cached content...")
            self.contents = open(cache_file, 'r').read()

        return self.contents
