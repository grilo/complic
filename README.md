# complic
Collects all licensing information reported by several package managers.

Matches those licenses with a backend to determine if the license is approved,
unapproved or unknown by your legal team.

Supported package managers:
  * mvn
  * npm
  * pypi

Supported backends:
  * Artifactory (I believe only the 'pro' version  comes with license control).

```
usage: main.py [-h] [-v] [-d DIRECTORY] [-f FORMAT]

Collects all licensing information reported by several package managers (mvn,
npm, pypi, etc.).

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Increase output verbosity
  -d DIRECTORY, --directory DIRECTORY
                        The directory to scan.
```

Simple example:
```
# Clone
git clone https://github.com/grilo/complic.git

# Install locally
cd complic
pip install .

# Run it
complic -d /some/project/dir
```

`complic` returns a non-zero exit status if any non-approved licenses are found.

Alternatives:
  * https://github.com/benbalter/licensee
  * https://github.com/nexB/scancode-toolkit
  * https://github.com/fossology/fossology (nomos)
  * https://wiki.debian.org/CopyrightReviewTools

Other tools have pretty exhaustive scan methods and detection heuristics. They
should be your first choice always.

`complic` only queries the application's package manager (multiple packages per
project are supported, though) for licensing information regarding all of its
dependencies.

The end result is a much faster execution time (a couple of minutes for
medium-sized projects) with a very high degree of reliability. Which is only
only possible if the maintainers of the dependencies your project uses are
careful enough to populate their package's metadata with such information.
