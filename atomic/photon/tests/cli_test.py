import io
import unittest
from collections import namedtuple
from unittest.mock import patch

import networkx as nx

from atomic.darkmatter import fileapi
from atomic.photon import cli


def assert_dict_in_dict(a, b):
    """Assert dict A is within dict B."""
    assert isinstance(a, dict) and isinstance(b, dict)
    for k, v in a.items():
        assert k in b
        assert a[k] == b[k]


class ReactorTestCase(unittest.TestCase):
    """Tests for the CLI and embedded client functions.

    There should be a test method for each command and its associated
    <subcommand>_cmd method.  Testing the actual command functions requires
    inspecting the Graph for changes. Testing the <subcommand>_cmd methods
    merely requires asserting the command functions were invoked with the
    expected arguments.
    """

    @classmethod
    def setUpClass(cls):
        cls.reactor = cli.Reactor(None).setup()

    def setUp(self):
        self.G = nx.DiGraph()
        self.api = fileapi.FileAPI(self.G, graphfile=None)
        self.reactor.api = self.api

    AddTestCase = namedtuple('AddTestCase',
                             ('name', 'args', 'funcargs', 'exp'))
    addTestCases = (
        AddTestCase(
            name='empty',  # Testcase identifier
            args=['add'],  # A la `sys.argv`; shell-parsed string input
            funcargs={'args': []},  # Subcommand func arguments
            exp=SystemExit("Missing args")  # Expected node OR error
        ),
        AddTestCase(
            name='simple',
            args=['add', 'cats'],
            funcargs={'args': ['cats']},
            exp={'uid': 1, 'name': 'cats'}
        ),
    )

    def test_add(self):
        for tc in self.addTestCases:
            self.reactor.out = io.StringIO()
            with self.subTest(name=tc.name):
                if isinstance(tc.exp, SystemExit):
                    raise unittest.SkipTest("Invalid CLI input")
                self.reactor.add(**tc.funcargs)

                assert 'Added node' in self.reactor.out.getvalue()
                assert self.G.node[1] == tc.exp

    def test_add_cmd(self):
        for tc in self.addTestCases:
            with self.subTest(name=tc.name):
                with patch.object(self.reactor, 'add', autospec=True) as fn:
                    if isinstance(tc.exp, SystemExit):  # Invalid input
                        with self.assertRaises(SystemExit):
                            self.reactor.process(tc.args)
                    else:  # Valid input
                        try:
                            self.reactor.setup()  # To register the mock
                            self.reactor.process(tc.args)
                            assert fn.call_count == 1  # called once
                            _, kw = fn.call_args  # kwargs
                            assert_dict_in_dict(tc.funcargs, kw)
                        except SystemExit as e:  # Catches SystemExit
                            self.fail("Parser choked: " % e)
