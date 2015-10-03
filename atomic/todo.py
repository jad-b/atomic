"""
todo
====

Everyone's got stuff to do.
"""

class Todo:

    def __init__(self, name, desc='', due=None):
        self.name = name
        self.desc = desc
        self.due = due

    def __str__(self):
        return "{due} {name}: {desc}".format(name=self.name, due=self.due, desc=self.desc)