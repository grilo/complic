# complic
Collects all licensing information reported by several package managers (mvn, npm, pypi, etc.).

This is a very basic implementation using Artifactory as a backend.

```
usage: main.py [-h] [-v] [-d DIRECTORY] [-f FORMAT]

Collects all licensing information reported by several package managers (mvn,
npm, pypi, etc.).

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Increase output verbosity
  -d DIRECTORY, --directory DIRECTORY
                        The directory to scan.
  -f FORMAT, --format FORMAT
                        The output format (csv, json or pretty).
```

Simple example: `python main.py -d <directory_with_project>`

Alternatives:
  * https://github.com/benbalter/licensee
  * https://github.com/nexB/scancode-toolkit
  * https://github.com/fossology/fossology (nomos)
  * https://wiki.debian.org/CopyrightReviewTools
