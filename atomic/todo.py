"""
todo
====

Everyone's busy. Be busy better.
"""
import json
from datetime import timedelta

import pytimeparse


class Todo:

    def __init__(self, name, desc='', due=None, data=None):
        """Create a todo item.

        :arg str name: One-line title of the todo.
        :kwarg str desc: Descriptive body for the todo.
        :kwarg ``datetime`` due: Due date of the todo.
        :kwarg ``object`` data: Any serializable object. Probably a string.
        """
        self.name = name
        self.desc = desc
        self.due = due
        self.data = data
        self.timelog = timedelta()
        self.tags = ()

    def __repr__(self):
        return "{due} {name}: {desc}".format(name=self.name, due=self.due,
                                             desc=self.desc)

    def __str__(self):
        return "{name}".format(name=self.name)

    def to_dict(self):
        return self.__dict__

    def to_json(self):
        data = dict(self.__dict__)
        data['timelog'] = str(self.timelog)
        return json.dumps(data)

    @classmethod
    def parse(cls, line, delim=';'):
        """Parse a Todo from a string.

        Assumes the same argument ordering as the :func:`Todo.__init__` method.
        Defaults to splitting on semi-colons.

        Accepted formats:
            <name>; <desc>; [<tags>]; <due>[;<ignored>]
        """
        parts = line.split(delim)
        parse_fns = (
                identity,
                identity,
                # parse_tags,
        )

        # Map parsing functions against arguments
        args = []
        for i, part in enumerate(parts):
            args.append(parse_fns[i](part.strip()))

        return cls(*args)


def log(orig, delta):
    """Attach a logged amount of work on the todo."""
    if isinstance(delta, str):  # Convert to timedelta
        delta = timedelta(seconds=pytimeparse.parse(delta))
    assert isinstance(delta, timedelta)
    return orig + delta


def identity(x):
    return x
