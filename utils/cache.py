#!/usr/bin/env python

import logging
import os
import json
import time
import multiprocessing as mp

import requests


class Remote(object):

    def __init__(self, url=None, name='Cache'):
        self.url = url
        self.cache_dir = os.path.join(os.environ.get("HOME", os.getcwd()), '.complic', name)
        self.cache_ttl = 15811200  # Seconds
        self._licenses = {}

    def _refresh(self):
        raise NotImplementedError

    @property
    def licenses(self):
        """Layered approach for handling the cache:
        1. prefer local disk.
        2. if not found or expired, download it
        """

        lic_idx = os.path.join(self.cache_dir, 'licenses.json')

        # If local cache is invalid, rebuild it
        if not os.path.isfile(lic_idx) or \
            time.time() - os.path.getmtime(lic_idx) > self.cache_ttl:
            logging.warning("Cache invalid, downloading...")

            if not os.path.isdir(self.cache_dir):
                os.makedirs(self.cache_dir)

            lock = os.path.join(self.cache_dir, '.updating')
            if os.path.isfile(lock):
                return self._licenses
            open(lock, 'w').close()
            try:
                self._licenses = self._refresh()
            finally:
                os.remove(lock)

            with open(lic_idx, 'w') as lics:
                logging.info("Caching results...")
                json.dump(self._licenses, lics)

        # Return locally stored licenses
        if not self._licenses:
            logging.info("Retrieving cached licenses...")
            self._licenses = json.loads(open(lic_idx, 'r').read())

        return self._licenses
