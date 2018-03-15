#!/usr/bin/env python
"""
    Extract licensing information from python projects (with setup.py).

This looks more complex than it really is. Python package management
is a mess and this module reflects that. Tons of string parsing due to
"plaintext" formats being used everywhere.

Why not something reasonably structured? Even XML is better than this.

Python: there should be one obvious way to do it... except packaging.
"""

import logging
import re
import os
import sys
import distutils.spawn
import setuptools

from complic.utils import fs, shell

from . import base


class Scanner(base.Scanner):
    """Look for setup.py files.

    Generate pkg-info and start downloading all the dependencies
    if they don't exist in PYTHONPATH already. We ignore versions
    when handling the requirements, but since we handle each of
    those requirements individually, we may end up capturing
    different licenses for each one.
    """

    def __init__(self):
        super(Scanner, self).__init__()

        if distutils.spawn.find_executable('pip'):
            self.register_handler(re.compile(r'.*/setup.py$'),
                                  Scanner.handle_setuppy)
        else:
            logging.error("Unable to find 'pip' executable in PATH.")


    @staticmethod
    def parse_metadata(metadata):
        """Parses either PKG-INFO or METADATA python files."""
        regex_name = re.compile(r'^\s*Name: (.*).*$', flags=re.MULTILINE)
        regex_ver = re.compile(r'^\s*Version: (.*).*$', flags=re.MULTILINE)
        regex_lic = re.compile(r'^\s*License: (.*)$', flags=re.MULTILINE)
        name = regex_name.search(metadata).group(1)
        version = regex_ver.search(metadata).group(1)
        lic = regex_lic.search(metadata).group(1)

        return ':'.join(['python', name, version]), lic

    @staticmethod
    def get_extra_requirements(setup_py):
        """Parse/execute the setup.py file looking for 'extra_requirements'.

        Since the setup.py file is a python script, it can contain anything,
        beyond what a few regexes could ever hope to achieve. As such, we
        execute the file and obtain the final extras_require.

        The extras_require is then used to run a full "pip install" with
        all optional dependencies."""
        def mock_setup(**kwargs):
            mock_setup.extras = kwargs.get('extras_require', {}).keys()
        setuptools.setup = mock_setup
        sys.path = [os.path.dirname(setup_py)] + sys.path
        import setup # This triggers the execution of mock_setup
        sys.path = sys.path[1:] # Remove the taint from our environment
        return mock_setup.__dict__.get('extras', [])

    @staticmethod
    def pip_install(setup_py, extras=None):
        """Runs a pip install, with extra requirements if provided.

        Returns (bool) depending on the exit code."""

        with fs.chdir(os.path.dirname(setup_py)) as new_dir:
            build_dir = os.path.join(new_dir, 'builddir')
            os.makedirs(build_dir)
            command = "PYTHONUSERBASE='%s' " % (build_dir)
            command += "pip install --ignore-installed ."
            if extras:
                command += "[%s]" % (','.join(extras))

            logging.info("Running pip install on %s", new_dir)
            return_code, _, _ = shell.cmd(command, print_error=True)

            if return_code != 0:
                logging.error("Make sure ~/.pip/pip.conf is correctly configured.")
                return False
        return True

    @staticmethod
    def handle_setuppy(file_path):
        """Run the setup script and parse its requirements (dependencies).

        We build our own dependency tree and then flatten it before returning.

        The initial implementation was using python's infrastructure for
        package handling, but the plumbing is dreadful and the API completely
        unusable. So we opted to build our own.
        """
        logging.debug("Matched setup.py handler: %s", file_path)

        file_path = os.path.abspath(file_path)
        extra_requires = Scanner.get_extra_requirements(file_path)

        if not Scanner.pip_install(file_path, extra_requires):
            logging.error("Unable to run pip install for: %s", file_path)
            return []

        deps = []
        for path in fs.Find(os.path.dirname(file_path)).files:
            if not os.path.basename(path) in ['PKG-INFO', 'METADATA']:
                continue


            metadata = open(path, 'r').read()

            identifier, lic = Scanner.parse_metadata(metadata)
            dependency = base.Dependency(**{'path': path})
            dependency.identifier = identifier
            dependency.licenses.add(lic)
            deps.append(dependency)

        return deps
