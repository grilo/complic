#!/usr/bin/env python

import logging
import re
import os
import setuptools.sandbox
import pkg_resources
import copy
import pip
import zipfile
import tarfile

import scanner.base
import utils.fs


class Scanner(scanner.base.Scanner):

    @staticmethod
    def parse_metadata(meta):
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
            for req in Scanner.without_version(match):
                info['requirements'].add(req)

        info['identifier'] = info['name'] + ':' + info['version']

        return info

    @staticmethod
    def without_version(requires):
        deps = []
        regex = re.compile(r'^([A-Za-z0-9_\-\.]+).*$')
        for line in requires.splitlines():
            deps.append(regex.search(line).group(1))
        return deps


    def __init__(self, *args, **kwargs):
        super(Scanner, self).__init__(*args, **kwargs)

        self.register_handler(re.compile(r'.*/setup.py$'),
                              self.handle_setuppy)

        self.pkgdb = {}
        for dist in pkg_resources.working_set:
            for metafile in ['PKG-INFO', 'METADATA']:
                if dist.has_metadata(metafile):
                    pkginfo = Scanner.parse_metadata(dist.get_metadata(metafile))
            self.pkgdb[pkginfo['name']] = pkginfo

    def __download(self, pkgname):
        old_dir = os.getcwd()
        with utils.fs.TemporaryDirectory() as tmp:
            os.chdir(tmp)
            logging.info("Downloading package and dependencies: %s", pkgname)
            rc = pip.main(['-q', 'download', pkgname])
            for archive in utils.fs.Find(tmp).files:
                if archive.endswith('.whl'):
                    wheel = zipfile.ZipFile(archive)
                    for f in wheel.namelist():
                        if f.endswith('METADATA'):
                            pkginfo = Scanner.parse_metadata(wheel.open(f, 'r').read())
                            self.pkgdb[pkginfo['name']] = pkginfo
                elif archive.endswith('gz'):
                    tarball = tarfile.open(archive)
                    for f in tarball.getnames():
                        if f.endswith('PKG-INFO'):
                            pkginfo = Scanner.parse_metadata(tarball.extractfile(f).read())
                            self.pkgdb[pkginfo['name']] = pkginfo
        os.chdir(old_dir)

    def __deptree(self, pkgname, dependencies):
        if pkgname in dependencies:
            return {}

        if pkgname not in self.pkgdb:
            logging.warning("No local metadata for dependency: %s", pkgname)
            self.__download(pkgname)

        pkginfo = self.pkgdb[pkgname]

        dep = scanner.base.Dependency('metadata')
        dep.identifier = pkginfo['identifier']
        dep.licenses.add(pkginfo['license'])
        dependencies[dep.identifier] = dep

        for req in pkginfo['requirements']:
            dependencies.update(self.__deptree(req, dependencies))
        return dependencies

    def handle_setuppy(self, file_path):
        logging.debug("Matched setup.py handler: %s", file_path)

        # Generate a <package>.egg-info/PKG-INFO which we can parse
        setuptools.sandbox.run_setup(file_path, ['egg_info'])

        pkginfo = {}
        for path in utils.fs.Find(os.path.dirname(file_path)).files:
            if path.endswith('PKG-INFO') or path.endswith('METADATA'):
                pkginfo.update(Scanner.parse_metadata(open(path, 'r').read()))

        for path in utils.fs.Find(os.path.dirname(file_path)).files:
            if path.endswith('requires.txt'):
                for line in open(path, 'r').read().splitlines():
                    for dep in Scanner.without_version(line):
                        pkginfo['requirements'].add(dep)

        # We now have the initial list of dependencies. Run through all of
        # them recursively to find out their licenses.
        dependencies = {}
        for req in pkginfo['requirements']:
            dependencies.update(self.__deptree(req, dependencies))

        return dependencies.values()
