from collections import namedtuple

import networkx as nx

from atomic import parse, fileapi


def test_time_parsing():
    # Get current local time
    # today = parse.starting_date()
    dt_inputs = (
        "14:02",
        "2:02 pm",
        "2015 Nov 16",
        "14",
        "Dec 14",
        "2015 Dec 14",
        "2015 Dec 14 14:02",
    )
    for testcase in dt_inputs:
        parse.parse_datetime(testcase)


def test_parse_key_values():
    TestData = namedtuple('TestData', ['input', 'out'])
    testcases = (
        TestData('', {}),
        TestData('body=', {'body': ''}),
        TestData('body= cats=two', {'body': '', 'cats': 'two'}),
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

sample_markdown = """
Header 1
========
## Header 2

* todo21

## Header 3

* todo31
    * todo311
        * todo3111
        * todo3112
    * todo312
""".strip()

nested_list = """
* t1
  * t11
    * t111
""".strip()


def test_markdown_to_graph():
    api = fileapi.FileAPI(G=nx.DiGraph())
    parse.import_markdown(api, nested_list)

    todo21 = api.Node.get(0)  # todo21
    assert 'Header1' in todo21
    assert 'Header2' in todo21

    todo31 = api.Node.get('todo31')
    assert 'Header1' in todo31
    assert 'Header3' in todo31

    edges = (
        ('todo31', 'todo311'),
        ('todo311', 'todo3111'),
        ('todo311', 'todo3112'),
        ('todo31', 'todo312')
    )
    for src, dest in edges:
        assert api.Edge.get(src, dest) is not None
