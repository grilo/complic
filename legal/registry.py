#!/usr/bin/env python

import logging
import os
import json
import time
import multiprocessing as mp

import requests


class Base(object):

    def __init__(self, url=None):
        self.url = url
        self.cache_dir = os.path.join(os.environ.get("HOME", os.getcwd()), '.complic', self.__class__.__name__)
        self.cache_ttl = 15811200  # Seconds
        self._licenses = {}

    def _refresh_cache(self):
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
            self._licenses = self._refresh_cache()
            os.remove(lock)

            with open(lic_idx, 'w') as lics:
                logging.info("Caching results...")
                json.dump(self._licenses, lics)

        # Return locally stored licenses
        if not self._licenses:
            logging.info("Retrieving cached licenses...")
            self._licenses = json.loads(open(lic_idx, 'r').read())

        return self._licenses


class SPDX(Base):
    """Returns all SPDX licenses, built-in cache mechanism.

    Handles like an immutable dictionary.
    """

    def __init__(self):
        super(SPDX, self).__init__(url='https://spdx.org/licenses')

    def _refresh_cache(self):
        lics = {}
        results = requests.get(self.url).json()
        details = [lic['detailsUrl'] for lic in results['licenses']]

        logging.info("Downloading (%s) licenses from: %s", len(details), self.url)

        pool = mp.Pool()
        for response in pool.imap_unordered(requests.get, details):
            license = response.json()
            logging.debug("Downloaded: %s", license['licenseId'])
            lics[license['licenseId']] = license
        pool.close()
        pool.join()

        return lics


class Artifactory(Base):
    """Returns all Artifactory licenses, built-in cache mechanism.

    Handles like an immutable dictionary.

    Note that we're using a "non-public" API of artifactory.
    """

    def __init__(self, url='http://artifactory:8080/artifactory/ui/licenses/crud'):
        super(Artifactory, self).__init__(url=url)

    def _refresh_cache(self):
        return json.loads(open('/home/grilo/projects/complic/jaylics', 'r').read())
