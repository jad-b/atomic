import io
import shlex
import unittest
from collections import namedtuple
from functools import partial
from unittest.mock import patch

import networkx as nx

from atomic.darkmatter import fileapi
from atomic.photon import cli
from atomic.errors import AtomicError


def assert_dict_in_dict(a, b):
    """Assert dict A is within dict B."""
    assert isinstance(a, dict) and isinstance(b, dict)
    for k, v in a.items():
        assert k in b
        assert a[k] == b[k], str(b)


class ReactorTestCase(unittest.TestCase):
    """Tests for the CLI and embedded client functions.

    There should be a test method for each command and its associated
    <subcommand>_cmd method.  Testing the actual command functions requires
    inspecting the Graph for changes. Testing the <subcommand>_cmd methods
    merely requires asserting the command functions were invoked with the
    expected arguments.

    See the 'add' command tests for how the tests are engineered, as they've
    been given extra effort regarding their description.
    """

    @classmethod
    def setUpClass(cls):
        cls.reactor = cli.Reactor(None).setup()

    def setUp(self):
        self.G = nx.DiGraph()
        self.api = fileapi.FileAPI(self.G)
        self.reactor.api = self.api

    AddTestCase = namedtuple(
        'AddTestCase', (
            'name',  # str: Testcase identifier
            'history',  # list[func]: List of test state setup functions
            'cli_args',  # str: A la `sys.argv`; shell-parsed string input
            'err',  # SystemExit or AtomicError
            'func_kwargs',  # dict: Subcommand func keyword arguments
            'exp_state'  # dict: Expected state of the Graph. If uid is
                         # missing, it will be set to the return.
        )
    )
    addTestCases = (
        AddTestCase(
            name='empty',
            history=[],
            cli_args='add',
            err=SystemExit("Missing args"),
            func_kwargs=None,
            exp_state=None
        ),
        AddTestCase(
            name='simple',
            history=[],
            cli_args='add cats',
            func_kwargs={'args': ['cats']},
            exp_state={'name': 'cats'},
            err=None
        ),
        AddTestCase(
            name='Name with spaces',
            history=[],
            cli_args='add A Longer Name',
            func_kwargs={'args': ['A', 'Longer', 'Name']},
            exp_state={'name': 'A Longer Name'},
            err=None
        ),
        AddTestCase(
            name='Parent given',
            history=[fileapi.FileNodeAPI.create],
            cli_args='add -p 1 Child',
            func_kwargs={'parent': 1, 'args': ['Child']},
            exp_state={'name': 'Child'},
            err=None
        ),
        AddTestCase(
            name='Nonexistent Parent',
            history=[],
            cli_args='add -p 9999 Child',
            func_kwargs={'parent': 9999, 'args': ['Child']},
            exp_state={'name': 'Child'},
            err=AtomicError
        ),
        AddTestCase(
            name='KVs_and_tag',
            history=[],
            cli_args='add cats key=value tag=',
            func_kwargs={'args': ['cats', 'key=value', 'tag=']},
            exp_state={'name': 'cats', 'key': 'value', 'tag': ''},
            err=None
        ),
        AddTestCase(
            name='KV with spaces and tag',
            history=[],
            cli_args='add cats key=value with spaces tag=',
            func_kwargs={'args': ['cats', 'key=value', 'with', 'spaces',
                                  'tag=']},
            exp_state={'name': 'cats', 'key': 'value with spaces', 'tag': ''},
            err=None
        ),
    )

    def test_add_cmd(self):
        """Test for the 'atomic add' CLI subcommand."""
        for tc in self.addTestCases:
            with self.subTest(name=tc.name):
                with patch.object(self.reactor, 'add', autospec=True) as fn:
                    # On invalid input, the CLI raises a SystemExit
                    if isinstance(tc.err, SystemExit):
                        with self.assertRaises(SystemExit):
                            self.reactor.process(tc.func_kwargs)
                    else:  # Valid input
                        try:
                            self.reactor.setup()  # To register the mock
                            self.reactor.process(shlex.split(tc.cli_args))
                            assert fn.call_count == 1  # called once
                            _, kw = fn.call_args  # kwargs
                            assert_dict_in_dict(tc.func_kwargs, kw)
                        except SystemExit as e:  # Catches SystemExit
                            self.fail("Parser choked on: " % e)

    def test_add(self):
        """Test for the 'atomic add' procedure."""
        for tc in self.addTestCases:

            if isinstance(tc.err, SystemExit):
                continue  # Skip tests for invalid CLI input

            for fn in tc.history:
                fn(self.api.Node)

            self.reactor.out = io.StringIO()
            with self.subTest(name=tc.name):
                if tc.err:
                    # import pdb
                    # pdb.set_trace()
                    with self.assertRaises(tc.err):
                        self.reactor.add(**tc.func_kwargs)
                else:
                    uid = self.reactor.add(**tc.func_kwargs)
                    exp = dict(tc.exp_state)
                    exp.setdefault('uid', uid)
                    assert 'Added node' in self.reactor.out.getvalue()
                    assert self.G.node[uid] == exp

    ShowTestCase = namedtuple(
        'ShowTestCase', (
            'name',
            'history',
            'cli_args',
            'err',
            'func_kwargs',
            'exp'
        )
    )
    showTestCases = (
        ShowTestCase(
            name='missing id',
            history=[],
            cli_args='show',
            err=SystemExit(),
            func_kwargs=None,
            exp=None
        ),
        ShowTestCase(
            name='not found',
            history=[],
            cli_args='show 3',
            func_kwargs={'uid': 3},
            err=AtomicError,
            exp=None
        ),
        ShowTestCase(
            name='basic',
            history=[partial(fileapi.FileNodeAPI.create, name='basic')],
            cli_args='show 1',
            func_kwargs={'uid': 1},
            exp={'uid': 1, 'name': 'basic'},
            err=None,
        ),
    )

    def test_show_cmd(self):
        """Tests for the 'atomic show' CLI subcommand."""
        for tc in self.showTestCases:
            with self.subTest(name=tc.name):
                with patch.object(self.reactor, 'show', autospec=True) as fn:
                    # On invalid input, the CLI raises a SystemExit
                    if isinstance(tc.err, SystemExit):
                        with self.assertRaises(SystemExit):
                            self.reactor.process(tc.func_kwargs)
                    else:  # Valid input
                        try:
                            self.reactor.setup()  # To register the mock
                            self.reactor.process(shlex.split(tc.cli_args))
                            assert fn.call_count == 1  # called once
                            _, kw = fn.call_args  # kwargs
                            assert_dict_in_dict(tc.func_kwargs, kw)
                        except SystemExit as e:  # Catches SystemExit
                            self.fail("Parser choked on: " % e)

    def test_show(self):
        """Test for the 'atomic show' procedure."""
        for tc in self.showTestCases:
            if isinstance(tc.err, SystemExit):
                continue  # Skip tests for invalid CLI input

            for fn in tc.history:
                fn(self.api.Node)

            self.reactor.out = io.StringIO()
            with self.subTest(name=tc.name):
                # import pdb
                # pdb.set_trace()
                if tc.err:
                    with self.assertRaises(tc.err):
                        self.reactor.show(**tc.func_kwargs)
                else:
                    self.assertDictEqual(tc.exp,
                                         self.reactor.show(**tc.func_kwargs))
                    # assert 'Added node' in self.reactor.out.getvalue()

    ListTestCase = namedtuple(
        'ListTestCase', (
            'name',   # str: Name of testcase
            'history',  # List[fn]: Pre-test state setup, as curried functions
            'cli_args',  # str: CLI command
            'err',  # Exception: Expected exception to be raised
            'func_kwargs',  # dict: Keyword arguments to command function
            'exp'  # obj: Expected return from command
        )
    )
    listTestCases = (
        ListTestCase(
            name='no nodes in graph',
            history=[],
            cli_args='list',
            err=None,
            func_kwargs={},
            exp=None
        ),
        ListTestCase(
            name='one node',
            history=[partial(fileapi.FileNodeAPI.create, name='one node')],
            cli_args='list',
            err=None,
            func_kwargs=None,
            exp=[{'uid': 1, 'name': 'one node'}]
        ),
        ListTestCase(
            name='three nodes',
            history=[partial(fileapi.FileNodeAPI.create, name='one'),
                     partial(fileapi.FileNodeAPI.create, name='two'),
                     partial(fileapi.FileNodeAPI.create, name='three')],
            cli_args='list',
            err=None,
            func_kwargs=None,
            exp=[
                    {'uid': 1, 'name': 'one'},
                    {'uid': 2, 'name': 'two'},
                    {'uid': 3, 'name': 'three'},
                ]
        ),
    )

    def test_list_cmd(self):
        for tc in self.listTestCases:
            with self.subTest(name=tc.name):
                with patch.object(self.reactor, 'list', autospec=True) as fn:
                    # On invalid input, the CLI raises a SystemExit
                    if isinstance(tc.err, SystemExit):
                        with self.assertRaises(SystemExit):
                            self.reactor.process(tc.func_kwargs)
                    else:  # Valid input
                        try:
                            self.reactor.setup()  # To register the mock
                            self.reactor.process(shlex.split(tc.cli_args))
                            assert fn.call_count == 1  # called once
                            _, kw = fn.call_args  # kwargs
                            assert_dict_in_dict(tc.func_kwargs, kw)
                        except SystemExit as e:  # Catches SystemExit
                            self.fail("Parser choked on: " % e)

    def test_list(self):
        for tc in self.listTestCases:
            if isinstance(tc.err, SystemExit):
                continue  # Skip tests for invalid CLI input

            for fn in tc.history:
                fn(self.api.Node)

            with self.subTest(name=tc.name):
                if tc.err:
                    with self.assertRaises(tc.err):
                        self.reactor.list(**tc.func_kwargs)
                else:
                    self.assertListEqual(tc.exp,
                                         self.reactor.list(**tc.func_kwargs))
