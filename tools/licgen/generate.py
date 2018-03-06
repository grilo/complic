#!/usr/bin/env python

"""
    Downloads the SPDX license registry.

    Merges with our own license registry which:
        * Contains a few more.
        * Adds regexes to match the licenses.

    Also, runs all regex tests to ensure they aren't ambiguous:
        * A license regex must match exactly one license.
        * 0 matches = error, > 1 match = error
"""

import logging
import json
import re
import sys
import collections

import requests

logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s')
logging.getLogger().setLevel(logging.DEBUG)


licenses = json.loads(open('licenses.json', 'r').read())
raw_spdx = requests.get('https://raw.githubusercontent.com/spdx/license-list-data/master/json/licenses.json').json()
logging.info("SPDX licenses downloaded: %i", len(raw_spdx['licenses']))

for lic in raw_spdx['licenses']:
    lic['spdx'] = True
    lic['licenseId'] = lic['licenseId'].upper()
    identifier = lic['licenseId']
    if not identifier in licenses.keys():
        logging.warning("New SPDX license found: %s", identifier)
        licenses[identifier] = {}
        licenses[identifier]['regexp'] = lic['name']
    licenses[identifier].update(lic)

# We test this by running all "name" keys against all regexps found
errors = 0
for licenseId, license in licenses.items():
    if 'regexp' not in license:
        continue

    regexp = re.compile(license['regexp'], flags=re.IGNORECASE)

    self_test = False

    for lic in licenses.values():
        if 'name' not in lic:
            print lic
            logging.critical("Can't find 'name' in license struct: %s", lic['licenseId'])
            sys.exit(1)
        if not regexp.match(lic['name']):
            continue

        if lic['licenseId'] == licenseId:
            self_test = True
            continue

        if 'spdx' in lic and 'spdx' in license:
            logging.warning("Ignoring ambiguous SPDX licenses: %s <=> %s", licenseId, lic['licenseId'])
            continue
        elif lic['licenseId'].endswith('-ONLY') or licenseId.endswith('-ONLY'):
            logging.warning("Regex is ambiguous and has too many matches: %s (also matches: %s)", licenseId, lic['licenseId'])
            continue

        logging.error("Regex is ambiguous and has too many matches: %s (also matches: %s)", licenseId, lic['licenseId'])
        logging.error("\tTEXT: %s", lic['name'])
        logging.error("\tREGEXP: %s", license['regexp'])
        errors += 1
        sys.exit()

    if not self_test:
        logging.error("Regex doesn't match itself: %s", licenseId)
        logging.error("\tTEXT: %s", license['name'])
        logging.error("\tREGEXP: %s", license['regexp'])
        sys.exit()

if errors:
    logging.critical("Errors found, licenses.json not refreshed.")
    sys.exit(errors)


logging.info("Sorting licenses alphabetically.")

sorted_lics = collections.OrderedDict()

for k in sorted(licenses):
    lic = licenses[k]
    k = k.upper()
    lic['licenseId'] = k
    sorted_lics[k] = lic

print json.dumps(sorted_lics, indent=2)

