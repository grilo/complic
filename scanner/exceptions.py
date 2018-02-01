#!/usr/bin/env python

class MalformedBuildFileError(Exception):
    """When the package.json/pom.xml/etc. doesn't contain the expected attributes."""
    pass
