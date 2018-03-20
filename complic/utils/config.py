#!/usr/bin/env python
"""Configuration manager."""

import ConfigParser
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

        defaults = {}
        self.options = defaults

        if not config_file:
            config_file = os.path.join(os.environ.get("HOME", os.getcwd()),
                                       '.complic',
                                       'site.cfg')

        self.config_file = config_file
        config_dir = os.path.dirname(self.config_file)
        if not os.path.isdir(config_dir):
            os.makedirs(os.path.dirname(self.config_file))

        self.config_parser = ConfigParser.SafeConfigParser()
        if os.path.isfile(self.config_file):
            logging.info("Found config file: %s", self.config_file)
            self.config_parser.read(self.config_file)

        for section in self.config_parser.sections():
            if section not in self.options:
                self.options[section] = {}

            for key, value in self.config_parser.items(section):
                self.options[section][key] = value

        for section in self.options:
            for key, value in self.options[section].items():
                env_var = '_'.join([section.upper(), key.upper()])
                if os.environ.get(env_var):
                    logging.debug("ENV value found: %s", env_var)
                    self.options[section][key] = os.environ.get(env_var)


    def __getitem__(self, key):
        if not key in self.options:
            raise KeyError("Unable to find: %s" % (key))
        return self.options[key]

    def __setitem__(self, key, value):
        self.options[key] = value
        with open(self.config_file, 'w') as cfg:
            self.config_parser.write(cfg)
        return self.options[key]

    def __iter__(self):
        for key in self.options:
            yield key
