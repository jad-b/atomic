import pytest
import networkx as nx

from atomic.graph import graph


@pytest.fixture
def G():
    """Basic test Graph.

       1      # 0
     2   3    # 1
    4 5   6   # 2
         7 8  # 3
    """
    sample_graph = nx.DiGraph()
    for n in range(1, 9):
        sample_graph.add_node(n, {'uid': n})
    sample_graph.add_edges_from([
        (1, 2),
        (1, 3),
        (2, 4),
        (2, 5),
        (3, 6),
        (6, 7),
        (6, 8)
    ], type=graph.EdgeTypes.parent.name)
    yield sample_graph
