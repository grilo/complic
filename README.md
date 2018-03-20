# complic
Collects all licensing information reported by several package managers.

[![Build
Status](https://travis-ci.org/grilo/complic.svg)](https://travis-ci.org/grilo/complic)
[![Coverage Status](https://coveralls.io/repos/github/grilo/complic/badge.svg)](https://coveralls.io/github/grilo/complic)

Matches those licenses with a backend to determine if the license is approved,
unapproved or unknown by your legal team.

Supported package managers:
  * mvn
  * npm
  * pypi
  * cocoapods

Supported backends:
  * ~~Artifactory (I believe only the 'pro' version  comes with license control).~~
Backend support was disabled, everything is now builtin.

# Usage
```
# Install it
pip install --user git+https://github.com/grilo/complic

# Run it
complic -d /some/project/dir
```

A `complic-report.json` file will be generated in `/some/project/dir`. This
file contains information about:
  * Which licenses are being used.
  * Which of those licenses is known to complic.
  * What license is each dependency using.

Any "problems" found means potential non-complicance issues (usually unknown
licenses).

`complic` returns a non-zero exit status if the execution itself presents
problems. Compliance issues do **not** cause errors.

# Configuration
During runtime, `complic` will look for a ~/.complic/config.json file.

The schema for this file is described with some detail in the source code
(look for config.py), but the gist is:
```json
{
  "dependencies": {
    {
      "some:dependency": "some_license"
    }
  }
  "forbidden": [
    "AGPL-V1"
  ]
}
```

## Dependencies

Forces "some:dependency" to always be interpreted as having "some_license",
in spite of whatever the package manager returns. Regexes are supported for
the "some:dependency" part, allowing you to easily exclude packages from your
org. Example: `java:my.org.*: WTFPL`

## Forbidden
Whenever this license is found, it's reported as a "problem". Although the
concept of "license virality" has been debunked, it's still useful if you
the paranoid kind. Simply forbid them and have the dependencies using
that specific license be reported as "problems".

The actual license should match complic's internal inventory
(see: `complic/licenses/inventory.json`).

# Rationale

The actual risk of being accidentally non-compliant is often negligible. It
takes some intentional effort to take someone else's source code and modify
it voluntarily and **also** having it marked as a dependency.

In addition, compliance vs non-compliance discussion often depends on the
service model. Is the app being distributed within the same legal entity?
Is it a web service? Even if you infringe on a license, you can still get
away with it legally if you choose the correct service model.

In regulated environments, some degree of control over what licenses your
dependencies are using is mandatory in case you have issues down the line.
This will help you provide evidence of best-effort measures taken to
minimize any putative infringement.

# Roadmap

  * Add support for more package managers.
  * Python 3+.

Contributions very welcome.

# Prior art

  * https://github.com/benbalter/licensee
  * https://github.com/nexB/scancode-toolkit
  * https://github.com/fossology/fossology (nomos)
  * https://wiki.debian.org/CopyrightReviewTools

Other tools have pretty exhaustive scan methods and detection heuristics. Some
even have built-in license management. They should be your first choice always.

`complic` only queries the application's package manager (multiple packages per
project are supported, though) for licensing information regarding all of its
dependencies.

The end result is a much faster execution time (a couple of minutes for
large projects) with a decent degree of trustability. This is only possible
if the maintainers of your project's dependencies are careful enough to
populate their package's metadata with such information.
