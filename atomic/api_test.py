import pytest
import networkx as nx


@pytest.mark.yield_fixture
def graph():
    sample_graph = nx.MultiDiGraph()
    sample_graph.add_nodes_from(range(0, 7))
    sample_graph.add_edges_from([
        (1, 2),
        (1, 3),
        (2, 4),
        (5, 6)
    ])
    print("Initialized graph")
    return sample_graph
