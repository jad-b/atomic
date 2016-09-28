"""
parse.py
========
Responsible for providing string-parsing functions and regexes for
extracting REPL shell and CLI arguments into function arguments.
"""
import re
from datetime import datetime, date, time

import bs4
import mistune
from bs4 import BeautifulSoup


# key1=string key2=multi-word string...
PARSE_KEY_VALUE_RE = re.compile(
    r'\b([^\s]+)\s*=\s*([^=]*)(?=\s+\w+\s*=|$)')
# <src> <dest> <type> [key=value]...
PARSE_LINK_ARGS_RE = re.compile(
    r'(?P<src>\d+)\s+(?P<dest>\d+)\s+(?:type=)?(?P<type>\w+)\s*(?P<kwargs>.*)')


def parse_key_values(s):
    """Parse key-value pairs from 'key1=string key2=multi-word string ...'"""
    return {m.group(1): m.group(2) for m in PARSE_KEY_VALUE_RE.finditer(s)}


def parse_non_kv(s):
    """Parse _up_ to the first key=value; 'cats k=v' returns 'cats'."""
    m = PARSE_KEY_VALUE_RE.search(s)
    if m is None:
        return s
    return s[:m.start()].strip()


def parse_link_args(s):
    """Parse link arguments of the form '<src> <dest> <type> [key=value]...'"""
    match = PARSE_LINK_ARGS_RE.match(s)
    if match is None:
        raise ValueError("Unable to parse '{}' for linking".format(s))
    gd = match.groupdict()
    return int(gd['src']), int(gd['dest']), gd['type'], \
        parse_key_values(gd.get('kwargs', ''))


def input_bool(msg='Are you sure?', truths=('y', 'yes')):
    """Confirm action via the CLI."""
    b = input(msg + ' ')
    return b in truths


# Date & Time functions
timestamp_formats = (
    "%d",               # Day: 16
    "%b %d",            # Month day: Oct 16
    "%H:%M",            # Clock time: 14:02
    "%I:%M %p",         # 12-hour clock time: 2:02 PM
    "%Y %b %d",         # 2015 Oct 16
    "%Y %b %d %H:%M",   # 2015 Oct 16 08:52
)


def parse_datetime(line, formats=timestamp_formats):
    """Parses a timestamp from a string from a list of acceptable formats."""
    err = None
    for fmt in formats:
        try:
            return datetime.strptime(line, fmt)
        except ValueError as ve:
            err = ve
    if err:
        raise ValueError("Unable to parse '{}'".format(line))


def starting_date():
    # Use current year/month/day, and zero values for hours/min/ms
    return datetime.combine(date.today(), time())


def smart_date(dt):
    """Combine the parsed date/time/datetime with the current date to allow for
    shorthand date entry."""
    pass


def import_markdown(api, s):
    """Parse a markdown document into the graph.

    Only headers and list objects are used; the remainder is skipped.
    List items are created as nodes. Nested lists are interpreted as a parental
    hierarchy. Headers are attached to all following nodes as tags.
    """
    md = mistune.markdown(s)
    soup = BeautifulSoup(md, 'html.parser')
    _recursive_parse(api, soup.contents, MarkdownContext(), None)


class MarkdownContext:
    """Manage depth-based context from header tags in markdown.

    Example Markdown:

        # Header1
        ## Header2
        #### Header4

    Represents as the following internally:

        [Header1, Header2, None, Header4, None, None]

    Insertions clears the subsequent levels;
    thus, inserting at Header3 clears the array values of 3, 4, 5.
    """

    def __init__(self, size=6):
        self.size = size
        self._arr = [None] * size

    def clear(self, idx=0):
        self._arr[idx:] = [None] * (self.size - idx)

    def insert(self, idx, val):
        print("Inserting %s at %d; %s" % (val, idx, str(self._arr)))
        self._arr[idx-1] = val
        self.clear(idx)

    def get(self, idx=None):
        if idx:
            return self._arr[idx-1]
        return {x: '' for x in self._arr if x is not None}


def _recursive_parse(api, tags, ctx, parent=None):
    print("Parsing:\n%s\nparent=%s" % (tags,
                                       parent.string if parent else ''))
    last = None
    for c in tags:
        if not isinstance(c, bs4.element.Tag):
            continue
        print("Tag: %s=%s (parent=%s)" %
              (c.name, c.string, 'None' if parent is None else str(parent)))
        if c.name.startswith('h'):  # Save as tag
            idx = int(c.name[1:])  # Extract header depth from tag
            ctx.insert(idx,  c.string)
        elif c.name == 'ul' or c.name == 'ol':
            _recursive_parse(api, c.children, ctx, last)
        elif c.name == 'li':  # Add as node
            d = ctx.get()
            d['name'] = c.string   # Override the 'name' attribute
            uid = api.Node.add(parent, **d)
            print("Added uid=%d kwargs=%s" % (uid, d))
            last = uid  # Set ourselves as the last seen
            # In case the list has become nested within this list element:
            _recursive_parse(api, c.children, ctx, last)
