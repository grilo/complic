#!/usr/bin/env python

class MalformedProjectFileError(Exception):
    """When the package.json/pom.xml/etc. doesn't contain the expected attributes."""
    pass
