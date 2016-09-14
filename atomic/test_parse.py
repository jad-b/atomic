from collections import namedtuple

from atomic import parse


def test_parse_key_values():
    TestData = namedtuple('TestData', ['input', 'out'])
    testcases = (
        TestData('', {}),
        TestData("body=I don't know what to do with my hands",
                 {'body': "I don't know what to do with my hands"}),
        TestData("line1=I think line2=My fear's come true",
                 {'line1': 'I think', 'line2': "My fear's come true"})
    )
    for case in testcases:
        obs = parse.parse_key_values(case.input)
        assert case.out == obs


def test_parse_link_args():
    TestData = namedtuple('TestData', ['input', 'out'])
    testcases = (
        TestData(
            '0 1 cats',
            (0, 1, 'cats', {})
        ),
        TestData(
            '0 1 type=cats',
            (0, 1, 'cats', {})
        ),
        TestData(
            "0 1 type=cats body=I don't know what to do with my hands",
            (0, 1, 'cats', {'body': "I don't know what to do with my hands"})
        ),
        TestData(
            "0 1 type=cats line1=I think line2=My fear's come true",
            (0, 1, 'cats',
             {'line1': 'I think', 'line2': "My fear's come true"})
        )
    )
    for case in testcases:
        obs = parse.parse_link_args(case.input)
        assert case.out == obs
