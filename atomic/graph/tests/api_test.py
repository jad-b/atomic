import logging

import pytest

from atomic.darkmatter import fileapi
from atomic.errors import AtomicError


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
    assert nodeapi.get(uid) == {}


def test_update_node(nodeapi):
    data = {'name': test_update_node.__name__}
    uid = nodeapi.create(**data)

    newdata = dict(data)
    newdata['cats'] = True
    nodeapi.update(uid, **newdata)

    assert nodeapi.get(uid) == newdata
