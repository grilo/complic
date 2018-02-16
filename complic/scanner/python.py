#!/usr/bin/env python
"""
    Extract licensing information from python projects (with setup.py).

This looks more complex than it really is. Python package management
is a mess and this module reflects that. Tons of string parsing due to
"plaintext" formats being used everywhere.

What is wrong with all of XML, JSON and YAML? Why have something different?
"""

import logging
import re
import os
import zipfile
import tarfile
import subprocess
import pkg_resources
import setuptools.sandbox

import complic.scanner.base
import complic.utils.fs
import complic.utils.dictionary


class Scanner(complic.scanner.base.Scanner):
    """Look for setup.py files.

    Generate pkg-info and start downloading all the dependencies
    if they don't exist in PYTHONPATH already. We ignore versions
    when handling the requirements, but since we handle each of
    those requirements individually, we may end up capturing
    different licenses for each one.
    """

    @staticmethod
    def parse_metadata(meta):
        """Yay for weird formats."""
        regex_name = re.compile(r'^Name: (.*).*$', flags=re.MULTILINE)
        regex_vers = re.compile(r'^Version: (.*).*$', flags=re.MULTILINE)
        regex_lic = re.compile(r'^License: (.*)$', flags=re.MULTILINE)
        regex_req = re.compile(r'^Requires.*: ([A-Za-z0-9_\-\.]+).*$', flags=re.MULTILINE)
        info = {}
        info['name'] = regex_name.search(meta).group(1)
        info['version'] = regex_vers.search(meta).group(1)
        info['license'] = regex_lic.search(meta).group(1)
        info['requirements'] = set()

        for match in regex_req.findall(meta):
            info['requirements'].add(Scanner.without_version(match))

        info['identifier'] = info['name'] + ':' + info['version']

        return info

    @staticmethod
    def without_version(requires_line):
        """Removes the versioning stuff from a "requirements string".

        Example:
            >>> without_version("lambda>=1.0")
            lambda
        """
        regex = re.compile(r'^([A-Za-z0-9_\-\.]+).*$')
        match = regex.search(requires_line)
        return match.group(1)

    @staticmethod
    def __get_metadata(archive):
        """
            Handle both python package formats. We except a single metadata
            file in either of them.
        """
        if archive.endswith('.whl'):
            wheel = zipfile.ZipFile(archive)
            for compressed_file in wheel.namelist():
                if compressed_file.endswith('METADATA'):
                    return wheel.open(compressed_file, 'r').read()
        elif archive.endswith('gz'):
            tarball = tarfile.open(archive)
            for compressed_file in tarball.getnames():
                if compressed_file.endswith('PKG-INFO'):
                    return tarball.extractfile(compressed_file).read()
        return ''

    @staticmethod
    def __download(pkgname):
        old_dir = os.getcwd()
        with complic.utils.fs.TemporaryDirectory() as tmp:
            os.chdir(tmp)
            logging.debug("Downloading package and dependencies: %s", pkgname)
            # Running pip with -q messes with our logs
            # See: https://stackoverflow.com/questions/38754432
            log_level = logging.getLogger().level
            process = subprocess.Popen(["pip", "-q", "download", pkgname],
                                       shell=False,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            process.wait()

            logging.getLogger().setLevel(log_level)
            for archive in complic.utils.fs.Find(tmp).files:
                metadata = Scanner.parse_metadata(Scanner.__get_metadata(archive))
                yield metadata
        os.chdir(old_dir)

    def __init__(self):
        super(Scanner, self).__init__()

        self.register_handler(re.compile(r'.*/setup.py$'),
                              self.handle_setuppy)

        self.pkgdb = complic.utils.dictionary.LowerCase()
        for dist in pkg_resources.working_set: # pylint: disable=not-an-iterable
            for metafile in ['PKG-INFO', 'METADATA']:
                if dist.has_metadata(metafile):
                    metadata = Scanner.parse_metadata(dist.get_metadata(metafile))
            self.pkgdb[metadata['name']] = metadata

    def __deptree(self, pkgname, dependencies):

        pkgname = pkgname.replace('-', '_')

        if pkgname in dependencies:
            return {}

        if pkgname not in self.pkgdb:
            logging.debug("No local metadata for dependency: %s", pkgname)
            for metadata in Scanner.__download(pkgname):
                self.pkgdb[metadata['name']] = metadata

        metadata = self.pkgdb[pkgname]

        dep = complic.scanner.base.Dependency(**metadata)
        dep.identifier = 'python:' + metadata['identifier']
        dep.licenses.add(metadata['license'])
        dependencies[dep.identifier] = dep

        for req in metadata['requirements']:
            dependencies.update(self.__deptree(req, dependencies))
        return dependencies

    def handle_setuppy(self, file_path):
        """For each setup.py we get its requirements.

        To get a reliable requirements list we actually have to run the
        setup script fully. We have the sandbox method, though I have
        doubts whether it's really sandboxed or not.

        Still, we then handle each of those requirements, see if there
        is local information of that requirement and, if not, we download
        it using pip. Do it recursively until we're able to return a flat
        list of dependencies."""
        logging.debug("Matched setup.py handler: %s", file_path)

        file_path = os.path.abspath(file_path)

        # Generate a <package>.egg-info/PKG-INFO which we can parse
        setuptools.sandbox.run_setup(file_path, ['-q', 'egg_info'])

        metadata = {}
        for path in complic.utils.fs.Find(os.path.dirname(file_path)).files:
            if path.endswith('PKG-INFO') or path.endswith('METADATA'):
                metadata.update(Scanner.parse_metadata(open(path, 'r').read()))

        for path in complic.utils.fs.Find(os.path.dirname(file_path)).files:
            if path.endswith('requires.txt'):
                for line in open(path, 'r').read().splitlines():
                    metadata['requirements'].add(Scanner.without_version(line))

        # We now have the initial requirements. Run through all of
        # them recursively to find out their respective licenses.
        dependencies = {}
        for req in metadata['requirements']:
            dependencies.update(self.__deptree(req, dependencies))

        # In case multiple versions of the same dependency have different
        # licenses, we capture them all.
        for dependency in dependencies.values():
            lics = set()
            for lic in dependency.licenses:
                lics.add(lic)
            dependency.licenses = lics

        return dependencies.values()
