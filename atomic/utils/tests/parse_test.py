import textwrap
from collections import namedtuple

import networkx as nx

from atomic.utils import parse
from atomic.darkmatter import fileapi


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
                 {'line1': 'I think', 'line2': "My fear's come true"}),
        TestData("tag1= key1=value1 tag2=",
                 {'tag1': '', 'tag2': '', 'key1': 'value1'}),
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


MarkdownTestCase = namedtuple('MarkdownTestCase',
                              ['name', 'markdown', 'tuples', 'nodes', 'edges'])
__markdownTestCases = (
    MarkdownTestCase(
        name='1-level',
        markdown="""
        * t1
          * t11
        """,
        tuples=(
            (None, 't1', {}),
            ('t1', 't11', {})
        ),
        nodes=(
            (1, 't1'),  # (uid, name)
            (2, 't11'),
        ),
        edges=(
            (1, 2),  # (src, dest)
        )
    ),
    MarkdownTestCase(
        name='3-level',
        markdown="""
                 * t1
                  * t11
                  * t12
                    * t121
                 """,
        tuples=(
            (None, 't1', {}),
            ('t1', 't11', {}),
            ('t1', 't12', {}),
            ('t12', 't121', {}),
        ),
        nodes=(
            (1, 't1'),
            (2, 't11'),
            (3, 't12'),
            (4, 't121'),
        ),
        edges=(
            (1, 2),
            (1, 3),
            (3, 4)
        )
    ),
    MarkdownTestCase(
        name='complex',
        markdown="""
                 Header 1
                 ========
                 ## Header 2

                 * t1

                 ## Header 3

                 * t2
                     * t21
                         * t211
                         * t212
                     * t22
                 """,
        tuples=(
            (None, 't1', {'Header 1': None, 'Header 2': None}),
            (None, 't2', {'Header 1': None, 'Header 3': None}),
            ('t2', 't21', {'Header 1': None, 'Header 3': None}),
            ('t21', 't211', {'Header 1': None, 'Header 3': None}),
            ('t21', 't212', {'Header 1': None, 'Header 3': None}),
            ('t2', 't22', {'Header 1': None, 'Header 3': None}),
        ),
        nodes=(
            (1, 't1'),
            (2, 't2'),
            (3, 't21'),
            (4, 't211'),
            (5, 't212'),
            (6, 't22')
        ),
        edges=(
            (2, 3),
            (3, 4),
            (3, 5),
            (2, 6)
        )
    )
)


def test_recursive_parse():
    for testcase in __markdownTestCases:
        s = textwrap.dedent(testcase.markdown).strip()
        soup = parse._markdown_to_soup(s)
        ctx = parse.MarkdownContext()
        stream = parse._recursive_parse(soup.contents, ctx)
        for obs, exp in zip(stream, testcase.tuples):
            # print("Comparing %s v. %s" % (str(obs), str(exp)))
            assert obs == exp


def test_import_tuple_stream():
    for testcase in __markdownTestCases:
        G = nx.DiGraph()
        api = fileapi.FileAPI(G)
        parse._import_tuple_stream(api, testcase.tuples)
        for uid, name in testcase.nodes:
            assert uid in G
            assert G.node[uid]['name'] == name
        for src, dest in testcase.edges:
            assert src in G
            assert dest in G.edge[src]


def test_import_markdown():
    """Component test that black-boxes the subroutines."""
    for testcase in __markdownTestCases:
        G = nx.DiGraph()
        api = fileapi.FileAPI(G)
        s = textwrap.dedent(testcase.markdown).strip()
        parse.import_markdown(api, s)
        for uid, name in testcase.nodes:
            assert uid in G
            assert G.node[uid]['name'] == name
        for src, dest in testcase.edges:
            assert src in G
            assert dest in G.edge[src]
