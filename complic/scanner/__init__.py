#!/usr/bin/env python

from . import java, npm, python, cocoapods



def get():
    return [
        java.Scanner(),
        npm.Scanner(),
        python.Scanner(),
        cocoapods.Scanner(),
    ]
