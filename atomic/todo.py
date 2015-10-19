"""
todo
====

Everyone's got stuff to do.
"""

timestamp_formats = (
    "%d",               # Day: 16
    "%b %d",            # Month day: Oct 16
    "%H:%M",            # Clock time: 14:02
    "%I:%M %p",         # 12-hour clock time: 2:02 PM
    "%Y %b %d",         # 2015 Oct 16
    "%Y %b %d %H:%M",   # 2015 Oct 16 08:52
)

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
        self.tags = (,)

    def __repr__(self):
        return "{due} {name}: {desc}".format(name=self.name, due=self.due, desc=self.desc)
    def __str__(self):
        return "{name}".format(name=self.name)

    @classmethod
    def parse(cls, line, delim=';'):
        """Parse a Todo from a string.

        Assumes the same argument ordering as the :func:`Todo.__init__` method.
        Defaults to splitting on semi-colons.

        Accepted formats:
            <name>; <desc>; <due>; <ignored...>
        """
        parts = line.split(delim)
        identity_fn = lambda x: x
        parse_fns = (
                identity_fn,
                identity_fn,
                parse_datetime
        )

        # Map parsing functions against arguments
        args = []
        for i, part in enumerate(parts):
            args.append(parse_fns[i](part.strip()))

        return cls(*args)


def parse_datetime(line, formats=timestamp_formats):
    """Parses a timestamp from a string from a list of acceptable formats."""
    err = None
    for fmt in formats:
        try:
            return datetime.strptime(line, fmt)
        except ValueError as ve:
            err = ve
    else:
        if err:
            raise ve

def starting_date():
    # Use current year/month/day, and zero values for hours/min/ms
    today = datetime.combine(date.today(), time())

def smart_date(dt):
    """Combine the parsed date/time/datetime with the current date to allow for
    shorthand date entry."""

