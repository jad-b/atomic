import unittest

from todo import starting_date


class TestParsing(unittest.TestCase):

    def test_parsing_due_dates(self):
        # Get current local time
        today = starting_date()
        dt_inputs = (
            "14:02",
            "2:02 pm",
            "2015 Nov 16"
            "14",
            "Dec 14",
            "2015 Dec 14",
            "2015 Dec 14 14:02",
        )
