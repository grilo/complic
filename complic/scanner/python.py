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
import zipfile
import tarfile
import shlex
import subprocess
from pip._vendor import pkg_resources # pylint: disable=no-name-in-module
import setuptools.sandbox

import complic.utils.fs

from . import base


class Metadata(object):
    """Represents a generic python package."""

    @staticmethod
    def from_archive(path):
        """Support for both eggs and wheels."""
        if path.endswith('.tar.gz'):
            return Metadata.from_egg(path)
        elif path.endswith('.whl'):
            return Metadata.from_wheel(path)

    @staticmethod
    def from_wheel(wheel_path):
        """Extract all the metadata from a wheel archive.

        Returns a Metadata."""
        archive = zipfile.ZipFile(wheel_path)
        meta, reqs = '', ''
        for path in archive.namelist():
            if path.endswith('dist-info/METADATA'):
                meta = archive.open(path).read()
            elif path.endswith('dist-info/requires.txt'):
                reqs = archive.open(path).read()
        return Metadata(meta, reqs)

    @staticmethod
    def from_egg(egg_path):
        """Extract all the metadata from an egg archive.

        Returns a Metadata."""
        archive = tarfile.open(egg_path)
        meta, reqs = '', ''
        for path in archive.getnames():
            # Some really old packages might not even have egg-info/META
            if path.endswith('PKG-INFO'):
                meta = archive.extractfile(path).read()
            elif path.endswith('requires.txt'):
                reqs = archive.extractfile(path).read()
        return Metadata(meta, reqs)

    @staticmethod
    def from_setuppy(setup_path):
        """Generate a wheel binary distribution from a setup.py.

        Returns a Metadata."""

        log_level = logging.getLogger().level
        logging.getLogger().setLevel(50)
        try:
            setuptools.sandbox.run_setup(setup_path, ['-q', 'bdist_wheel'])
        except:
            raise IOError("Unable to correctly parse: %s" % (setup_path))
        finally:
            logging.getLogger().setLevel(log_level)
        basedir = os.path.join(os.path.dirname(setup_path), 'dist')
        regex = re.compile(basedir + r'.*\.whl')
        for path in complic.utils.fs.Find(basedir).files:
            if regex.match(path):
                return Metadata.from_wheel(path)

    def __init__(self, meta, requires=''):
        """Simplest way of parsing the metadata.

        The existing functions in wheel, pip and whatever just make the code
        much bigger due to all the different use cases they throw at us.
        """
        if not meta:
            raise AttributeError
        info = {}
        regex_name = re.compile(r'^Name: (.*).*$', flags=re.MULTILINE)
        regex_ver = re.compile(r'^Version: (.*).*$', flags=re.MULTILINE)
        regex_lic = re.compile(r'^License: (.*)$', flags=re.MULTILINE)
        regex_req = re.compile(r'^Requires.*: ([A-Za-z0-9_\-\.]+).*$',
                               flags=re.MULTILINE)
        info['name'] = regex_name.search(meta).group(1)
        info['version'] = regex_ver.search(meta).group(1)
        info['license'] = regex_lic.search(meta).group(1)
        info['identifier'] = 'py:' + info['name'] + ':' + info['version']

        info['requirements'] = []
        for req in regex_req.findall(meta):
            info['requirements'].append(pkg_resources.Requirement.parse(req))
        for req in requires.splitlines():
            if req and not req.startswith('['):
                info['requirements'].append(pkg_resources.Requirement.parse(req))
        self.info = info

    def __getattr__(self, key):
        return self.info[key]

    def __getitem__(self, key):
        return self.info[key]

    def to_dict(self):
        return self.info


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

        self.register_handler(re.compile(r'.*/setup.py$'),
                              self.handle_setuppy)

    @staticmethod
    def __download(requirement):
        """Download a package if not already present."""

        cache_dir = os.path.join(os.environ.get("HOME", os.getcwd()),
                                 '.complic', 'scanner', 'python')

        def find_cache(name):
            """Very basic caching mechanism."""
            safereq = name.replace('-', '.')
            regex = re.compile(cache_dir + '.' + safereq + r'\-.*(\.tar\.gz|\.whl)', re.IGNORECASE)
            for path in complic.utils.fs.Find(cache_dir).files:
                if regex.match(path):
                    return path

        cache = find_cache(requirement.name)
        if not cache:
            logging.debug("Downloading package: %s", requirement.name)
            # Running pip with -q messes with our logs
            # See: https://stackoverflow.com/questions/38754432
            log_level = logging.getLogger().level
            cmd = "pip -q download --no-deps -d " + cache_dir + " " + requirement.name
            process = subprocess.Popen(shlex.split(cmd),
                                       shell=False,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            process.wait()
            logging.getLogger().setLevel(log_level)
            cache = find_cache(requirement.name)
            if not cache:
                raise IOError
        return cache

    def build_tree(self, pkg, cyclic_path):
        """Generate a dependency tree.

        Recursively identify and download the requirements. We do this to
        have access to the License fields from each package's metadata.
        """
        dependencies = {}
        cyclic_path.append(pkg['name'])
        for req in pkg['requirements']:
            if req.name in cyclic_path:
                continue
            try:
                meta = Metadata.from_archive(Scanner.__download(req))
                dependencies[meta] = self.build_tree(meta, cyclic_path)
            except IOError:
                logging.debug("Unable to download: %s", req.name)
            except AttributeError:
                logging.debug("Unable to parse metadata: %s", req.name)
            finally:
                cyclic_path.append(req.name)
        return dependencies

    def flatten_tree(self, tree):
        """
            Transform:
                'hello': {
                    'world': {},
                }
            Into:
                ['hello', 'world']
        """
        values = set()
        for trunk, leaves in tree.items():
            values.add(trunk)
            for leaf in self.flatten_tree(leaves):
                values.add(leaf)
        return values

    def handle_setuppy(self, file_path):
        """Run the setup script and parse its requirements (dependencies).

        We build our own dependency tree and then flatten it before returning.

        The initial implementation was using python's infrastructure for
        package handling, but the plumbing is dreadful and the API completely
        unusable. So we opted to build our own.
        """
        logging.debug("Matched setup.py handler: %s", file_path)

        file_path = os.path.abspath(file_path)

        try:
            pkg = Metadata.from_setuppy(file_path)
        except IOError:
            return []

        dependency_tree = {}
        dependency_tree[pkg] = self.build_tree(pkg, [])

        dependencies = {}
        for leaf in self.flatten_tree(dependency_tree):
            dep = base.Dependency(**leaf.to_dict())
            dep.licenses = set()
            dep.licenses.add(leaf.license)
            dependencies[dep.identifier] = dep

        return dependencies.values()
