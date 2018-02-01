#!/usr/bin/env python


class Application(object):

    def __init__(self, path, licenses, identifier=None):
        self.path = path
        self.licenses = licenses
        self.identifier = identifier or path
