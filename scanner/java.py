#!/usr/bin/env python

import logging
import re
import os
import zipfile
import tempfile
import xml.etree.cElementTree as et
import shutil

import utils.fs
import scanner.base
import scanner.exceptions


class Scanner(scanner.base.Scanner):

    @staticmethod
    def _parse_manifest(string):
        manifest = {}
        lines = [l for l in string.splitlines() if l]
        for line in lines:
            splitted = line.split(': ')
            manifest[splitted[0]] = ': '.join(splitted[1:])

        coords = [
            'java',
            manifest.get('Bundle-SymbolicName',
                manifest.get('Group-Id',
                    manifest.get('Bundle-Vendor',
                        manifest.get('Implementation-Vendor-Id',
                            manifest.get('Implementation-Vendor', 'UnknownVendor'))))),
            manifest.get('Implementation-Title',
                manifest.get('Bundle-Name',
                    manifest.get('Application-Name', 'UnknownTitle'))),
            manifest.get('Implementation-Version',
                manifest.get('Bundle-Version',
                    manifest.get('Version', 'UnknownVersion'))),
        ]
        return ':'.join(coords)

    @staticmethod
    def _parse_pom(string):

        def update_gav(props, node):
            if node.tag == ns + 'artifactId':
                props['artifactId'] = node.text
            elif node.tag == ns + 'groupId':
                props['groupId'] = node.text
            elif node.tag == ns + 'version':
                props['version'] = node.text
            elif node.tag == ns + 'licenses':
                for license in node:
                    name = license.find(ns + 'name').text
                    url = license.find(ns + 'url').text
                    props['licenses'].append({
                        'name': name,
                        'url': url,
                    })
            return props

        props = {
            'artifactId': 'UnknownArtifactId',
            'groupId': 'UnkonwnGroupId',
            'version': 'UnknownVersion',
            'licenses': []
        }
        ns = "{http://maven.apache.org/POM/4.0.0}"
        root = et.fromstring(string)
        for node in root:
            # Also look in <parent>
            if node.tag == ns + 'parent':
                for child in node:
                    update_gav(props, child)
            else:
                update_gav(props, node)

        return props

    def __init__(self, *args, **kwargs):
        super(Scanner, self).__init__(*args, **kwargs)

        self.register_handler(re.compile(r'.*\.(e|j|w)ar$'),
                              self.handle_archive)
        self.register_handler(re.compile(r'.*(license|License|LICENSE).*'),
                              self.handle_license)
        self.register_handler(re.compile(r'.*\/META-INF\/MANIFEST\.(mf|MF)$'),
                              self.handle_manifest)
        self.register_handler(re.compile(r'.*\/pom.xml$'),
                              self.handle_pom)

    def handle_archive(self, file_path):
        logging.info("Scanning archive: %s", file_path)
        archive = zipfile.ZipFile(file_path)
        tempdir = tempfile.mkdtemp(prefix='complic')

        logging.debug("Exploding archive to temp dir: %s", file_path)
        archive.extractall(tempdir)
        results = self.scan(utils.fs.Find(tempdir).files)
        logging.debug("Removing tempdir: %s", tempdir)
        #shutil.rmtree(tempdir)
        return results

    def handle_manifest(self, file_path):
        logging.debug("Matched manifest handler: %s", file_path)
        result = scanner.base.Result(file_path)
        result.identifier = Scanner._parse_manifest(open(file_path, 'r').read())
        licfile = os.path.join(os.path.dirname(file_path), 'LICENSE.txt')
        if os.path.isfile(licfile):
            result.licenses.add(self.license_matcher.text(open(licfile, 'r').read()))
        return [result]

    def handle_license(self, file_path):
        logging.debug("Matched license handler: %s", file_path)
        result = scanner.base.Result(file_path)
        lic = self.license_matcher.text(open(file_path, 'r').read())
        result.licenses.add(lic)
        # Look for the closes MANIFEST or POM
        locations = [
            os.path.join(os.path.dirname(file_path), 'MANIFEST.MF'),
            os.path.join(os.path.dirname(file_path), 'META-INF', 'MANIFEST.MF'),
        ]
        for manifest_loc in locations:
            if os.path.isfile(manifest_loc):
                result.identifier = Scanner._parse_manifest(open(manifest_loc, 'r').read())
        return [result]

    def handle_pom(self, file_path):
        logging.debug("Matched pom handler: %s", file_path)
        props = Scanner._parse_pom(open(file_path, 'r').read())
        identifier = ':'.join([
            props['groupId'],
            props['artifactId'],
            props['version']
        ])

        result = scanner.base.Result(file_path)
        result.identifier = identifier
        for license in props['licenses']:
            result.licenses.add(self.license_matcher.name(license['name']))
            result.licenses.add(self.license_matcher.url(license['url']))
        if result.licenses:
            logging.info("Found POM with licensing info: %s", file_path)
        return [result]
