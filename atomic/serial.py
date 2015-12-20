#!/usr/bin/env python3
"""
serial
======

serial mimics the behavior of the serial type in postgresql, returning an auto-
incremented integer.
"""


class Serial:

    def __init__(self, start=0):
        self._index = start

    @property
    def index(self):
        self._index += 1
        return self._index

    def next(self):
        return self.index
