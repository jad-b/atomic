from datetime import datetime, date, time

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
    else:
        if err:
            raise ve


def starting_date():
    # Use current year/month/day, and zero values for hours/min/ms
    return datetime.combine(date.today(), time())


def smart_date(dt):
    """Combine the parsed date/time/datetime with the current date to allow for
    shorthand date entry."""
