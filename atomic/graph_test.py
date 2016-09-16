import pytest
import networkx as nx

from atomic import graph


@pytest.fixture
def G():
    """
       a      # 0
     b   c    # 1
    d e   f   # 2
         g h  # 3
    """
    sample_graph = nx.DiGraph()
    sample_graph.add_edges_from([
        ('a', 'b'),
        ('b', 'd'),
        ('b', 'e'),
        ('a', 'c'),
        ('c', 'f'),
        ('f', 'g'),
        ('f', 'h')
    ], type=graph.PARENT)
    yield sample_graph


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
        ('a', 0),
        ('b', 1),
        ('d', 2),
        ('e', 2),
        ('c', 1),
        ('f', 2),
        ('g', 3),
        ('h', 3)
    }
    obs = set(graph.hierarchy(G))
    assert obs == exp
