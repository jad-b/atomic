import io
from collections import namedtuple

import pytest

from atomic.darkmatter import fileapi
from atomic.photon import cli


@pytest.fixture()
def client(G):
    api = fileapi.FileAPI(G, graphfile=None)
    yield cli.CLIClient(api, file=io.StringIO())


def test_add(client):
    addTestCase = namedtuple('addTestCase',
                             ('args', 'parent', 'kwargs', 'exp'))
    testcases = (
        addTestCase([], None, {}, {'name': ''}),
    )
    for tc in testcases:
        client.file = io.StringIO()
        client.add(tc.args, tc.parent, **tc.kwargs)
        out = client.file.getvalue()

        assert 'Added node' in out
        curr = client.api.Node.serial.current  # Get last added serial
        tc.exp['uid'] = curr - 1
        assert client.api.G.node[curr-1] == tc.exp


def test_show(G, client):
    sio = io.StringIO()
    for n in G:
        client.file = sio
        client.show(n)
        # Assert node ID shows up in the output
        assert str(n) in sio.getvalue()
