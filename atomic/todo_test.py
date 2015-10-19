import unittest

from todo import Todo

class TestTodoParsing(unittest.TestCase):

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

class TestDatetimeParsing(unittest.TestCase):

    def test_parsing(self):
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


if __name__ == '__main__':
    unittest.main()

