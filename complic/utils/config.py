#!/usr/bin/env python
"""Configuration manager, implemented in json.


Schema:

    defaults = {
        'dependencies': {
            'some:identifier': 'spdx-identifier'
        },
        'forbidden': [
            'spdx-identifier-one'
        ]
    }

    dependencies { some:identifier { spdx-identifier
        Force "some:identifier" to always be parsed as having "spdx-identifier".
        Useful when the software is unable to properly identify a certain
        dependency's license. The "some:identifier" can be a regex.

        Example:
            "java:org.jenkins.*": "APACHE-2.0"
        This means that all "org.jenkins" dependencies found with the
        java scanner will be interpreted as having Apache 2.0 license.

    forbidden [ license, licese
        The specified licenses are always considered "Problem". Useful when
        you want a certain license to always raise an alert whenever its
        used.
"""

import json
import os
import logging


class Manager(object):
    """Wraps a very basic dictionary.

    Retrieves configuration from (in order of precedence):
        os.environ variables
        ~/.complic/site.cfg file
        defaults
    """

    def __init__(self, config_file=None):

        self.options = {
            'dependencies': {},
            'forbidden': [],
        }

        if not config_file: # pragma: nocover
            config_file = os.path.join(os.environ.get("HOME", os.getcwd()),
                                       '.complic',
                                       'config.json')

        self.config_file = config_file
        config_dir = os.path.dirname(self.config_file)
        if config_dir and not os.path.isdir(config_dir):
            os.makedirs(os.path.dirname(self.config_file))

        if os.path.isfile(self.config_file):
            logging.info("Found config file: %s", self.config_file)
            with open(self.config_file, 'r') as cfg:
                try:
                    self.options = json.loads(cfg.read())
                except ValueError as e:
                    logging.error("File is not valid JSON: %s", self.config_file)
                    raise e

    def __getitem__(self, key):
        if not key in self.options:
            raise KeyError("Unable to find: %s" % (key))
        return self.options[key]

    def __setitem__(self, key, value):
        self.options[key] = value
        with open(self.config_file, 'w') as cfg:
            cfg.write(json.dumps(self.options))
        return self.options[key]

    def __iter__(self):
        for key in self.options:
            yield key

    def keys(self):
        return self.options.keys()

    def items(self):
        return self.options.items()
