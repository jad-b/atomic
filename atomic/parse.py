"""
parse.py
========
Responsible for providing string-parsing functions and regexes for
extracting REPL shell and CLI arguments into function arguments.
"""
import re
from datetime import datetime, date, time

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
