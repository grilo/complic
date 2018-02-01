# Note: these are compiled with re.DOTALL

# See:
# https://github.com/spdx/license-list-data/blob/master/json/licenses.json
# https://github.com/spdx/license-list-data/tree/master/text

licenses = {
    'MIT': {
        'short': r'MIT',
        'long': r'.*MIT.*License.*Permission is hereby.*',
    },
    'APL': {
        'short': r'Apache-2.0',
        'long': r'(Apache License|The Apache)',
    },
    'UNLICENSE': {
        'short': r'Unlicense',
        'long': r'Unlicense',
    },
}
