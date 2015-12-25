import unittest

import networkx as nx

from atomic import graph

"""
0
1-2-4
 \
  3
5->6
"""


def initialize_graph():
    sample_graph = nx.DiGraph()
    sample_graph.add_nodes_from(range(0, 7))
    sample_graph.add_edges_from([
        (1, 2),
        (1, 3),
        (2, 4),
        (5, 6)
    ])
    print("Initialized graph")
    return sample_graph


class TestGraphOperations(unittest.TestCase):

    def setUp(self):
        self.graph = initialize_graph()

    def test_dfs_depth(self):
        """Test our dfs search returns a correctly-hierachied list of 2-tuples,
        containing (nodeId, depth)."""
        expected = [
            graph.NodeDepth(0, 0),
            graph.NodeDepth(1, 0),
            graph.NodeDepth(2, 1),
            graph.NodeDepth(4, 2),
            graph.NodeDepth(3, 1),
            graph.NodeDepth(5, 0),
            graph.NodeDepth(6, 1)
        ]
        dfs_results = graph.broad_dfs(self.graph, depth=True)
        print("Depth results returned")
        self.assertEqual(list(dfs_results), expected)
