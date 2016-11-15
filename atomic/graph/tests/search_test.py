import pytest

from atomic import graph


@pytest.mark.xfail(reason="Things have changed.")
def test_dfs_depth(G):
    """Test our dfs search returns a correctly-hierachied list of 2-tuples,
    containing (nodeId, depth).

    edges = [
        ('a', 'c'),  # a
        ('c', 'f'),  # a c
        ('f', 'g'),  # a c f
        ('f', 'h'),  # a c f
        ('a', 'b'),  # a
        ('b', 'd'),  # a b
        ('b', 'e')   # a b
        ]

    """
    exp = {
        (graph.Node(0, name='a'), 0),
        (graph.Node(1, name='b'), 1),
        (graph.Node(2, name='d'), 2),
        (graph.Node(3, name='e'), 2),
        (graph.Node(4, name='c'), 1),
        (graph.Node(5, name='f'), 2),
        (graph.Node(6, name='g'), 3),
        (graph.Node(7, name='h'), 3)
    }
    obs = set(graph.hierarchy(G))
    assert obs == exp
