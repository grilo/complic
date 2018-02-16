#!/usr/bin/env python
"""
Configuration manager.
"""

import ConfigParser
import os
import logging


class Manager(object):
    """Wraps a very basic dictionary.

    Retrieves configuration from (in order of precedence):
        os.environ variables
        ~/.complic/config file
        defaults
    """

    def __init__(self):
        default = {
            'artifactory': {
                'endpoint': 'https://artifactory:8080/artifactory/ui/licenses/crud',
                'username': 'admin',
                'password': 'admin',
            },
        }
        config_file = os.path.join(os.environ.get("HOME", os.getcwd()),
                                   '.complic',
                                   'site.cfg')
        config_parser = ConfigParser.SafeConfigParser()
        if os.path.isfile(config_file):
            logging.info("Found config file: %s", config_file)
            config_parser.read(config_file)

        for section, options in default.items():
            for key, value in options.items():
                env_var = '_'.join([section.upper(), key.upper()])
                if os.environ.get(env_var):
                    logging.debug("ENV value found: %s", env_var)
                    value = os.environ.get(env_var)
                else:
                    try:
                        value = config_parser.get(section, key)
                        logging.debug("CONFIG value found: %s", env_var)
                    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
                        logging.debug("DEFAULT value found: %s", key)
                setattr(self, env_var, value)

    def __getattr__(self, key):
        if '_' + key not in self.__dict__.keys():
            raise AttributeError("Config parameter not set: %s" % (key))
        return self.__dict__['_' + key]
