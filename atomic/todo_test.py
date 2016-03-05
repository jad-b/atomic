import unittest

from todo import Todo, todo_parser, starting_date


class TestParsing(unittest.TestCase):

    def test_name_parsing(self):
        test_inputs = (
                'Name of a thing',
                'Name of another thing;',
                'Name of another thing with trailing stuff;;;',
        )
        for i in test_inputs:
            with self.subTest(test_input=i):
                t = Todo.parse(i)
                exp = [x for x in i.split(';') if x][0]
                self.assertEqual(t.name == exp)

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


def test_cli_add(self):
    test_args = ('add', '-n', 'Test TODO')
    parser = todo_parser()
    args = parser.parse_args(test_args)
    assert args.name == 'Test TODO'
