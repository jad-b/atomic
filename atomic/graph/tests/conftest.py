import pytest
import networkx as nx

from atomic.graph import graph


@pytest.fixture
def G():
    """
       0      # 0
     1   2    # 1
    3 4   5   # 2
         6 7  # 3
    """
    sample_graph = nx.DiGraph()
    sample_graph.add_edges_from([
        (0, 1),
        (0, 2),
        (1, 3),
        (1, 4),
        (2, 5),
        (5, 6),
        (5, 7)
    ], type=graph.EdgeTypes.parent.name)
    yield sample_graph
