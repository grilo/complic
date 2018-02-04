#!/usr/bin/env python

import logging
import os
import json
import time
import multiprocessing as mp

import requests


class SPDX(object):
    """Returns all SPDX licenses, built-in cache mechanism.

    Handles like an immutable dictionary.
    """

    @staticmethod
    def _download_all(url):
        lics = {}
        results = requests.get(url).json()
        details = [lic['detailsUrl'] for lic in results['licenses']]

        logging.info("Downloading (%s) licenses from: %s", len(details), url)

        pool = mp.Pool()
        for response in pool.imap_unordered(requests.get, details):
            license = response.json()
            logging.debug("Downloaded: %s", license['licenseId'])
            lics[license['licenseId']] = license
        pool.close()
        pool.join()

        return lics


    def __init__(self, spdx_url='https://spdx.org/licenses', cache_dir=None):
        self.spdx_url = spdx_url
        if cache_dir is None:
            cache_dir = os.path.join(os.environ.get("HOME", os.getcwd()), '.complic')
        self.cache_dir = cache_dir
        self.cache_ttl = 15811200  # Seconds
        self._licenses = {}

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
            open(lock).close()
            self._licenses = self._download_all(os.path.join(self.spdx_url, 'licenses.json'))
            os.remove(lock)

            with open(lic_idx, 'w') as lics:
                logging.info("Caching results...")
                json.dump(self._licenses, lics)

        # Return locally stored licenses
        if not self._licenses:
            logging.info("Retrieving cached licenses...")
            self._licenses = json.loads(open(lic_idx, 'r').read())

        return self._licenses
