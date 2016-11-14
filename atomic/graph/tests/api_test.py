import logging

import pytest

from atomic.darkmatter import fileapi
from atomic.errors import AtomicError
from atomic.graph.graph import EdgeTypes


logger = logging.getLogger('test')


@pytest.fixture(params=[
    fileapi.FileNodeAPI,
], ids=[
    'fileapi'
])
def nodeapi(request, G):
    _api = request.param(G, logger)
    yield _api


def test_create_node(nodeapi):
    try:
        uid = nodeapi.create(name=test_create_node.__name__)
        assert isinstance(uid, int)
    except AtomicError as e:
        pytest.fail(e)


def test_get_node(nodeapi):
    data = dict(name=test_get_node.__name__)
    uid = nodeapi.create(**data)
    assert nodeapi.get(uid) == data


def test_delete_node(nodeapi):
    data = {'name': test_delete_node.__name__}
    uid = nodeapi.create(**data)
    nodeapi.delete(uid)
    assert nodeapi.get(uid) is None


def test_update_node(nodeapi):
    data = {'name': test_update_node.__name__}
    uid = nodeapi.create(**data)

    newdata = dict(data)
    newdata['cats'] = True
    nodeapi.update(uid, **newdata)

    assert nodeapi.get(uid) == newdata


@pytest.fixture(params=[
    fileapi.FileEdgeAPI,
], ids=[
    'fileapi'
])
def edgeapi(request, G):
    _api = request.param(G, logger)
    yield _api


def test_create_edge(edgeapi):
    with pytest.raises(AtomicError):  # Nodes shouldn't exist
        edgeapi.create(2**5, 2**6, type_=EdgeTypes.related.name)
    edgeapi.create(1, 2, type_=EdgeTypes.related.name,  # Look for exception
                   name=test_create_edge.__name__)


def test_get_edge(edgeapi):
    data = {
        'src': 4,
        'dst': 5,
        'type': EdgeTypes.related.name,
        'name': test_get_edge.__name__
    }
    edgeapi.create(**data)
    assert edgeapi.get(4, 5) == data


def test_delete_edge(edgeapi):
    edgeapi.create(3, 4, type_=EdgeTypes.related.name)
    edgeapi.delete(3, 4)
    assert edgeapi.get(3, 4) is None


def test_update_edge(edgeapi):
    data = {
        'src': 6,
        'dst': 7,
        'type': EdgeTypes.related.name,
        'name': test_update_edge.__name__
    }
    edgeapi.create(**data)
    newdata = dict(data)
    newdata['cats'] = True
    newdata['type'] = EdgeTypes.precedes.name

    edgeapi.update(**newdata)
    assert edgeapi.get(6, 7) == newdata
