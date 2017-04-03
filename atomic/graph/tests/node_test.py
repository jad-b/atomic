import unittest
from textwrap import dedent

from atomic.graph.graph import Node


class NodeTestCase(unittest.TestCase):

    def test_node_str(self):
        node = {
            "uid": 1,
            "name": "Floyd-Warshall",
            "type": "action"
        }
        exp = dedent(
            """
            [1] Floyd-Warshall
              type: action
            """).strip()
        obs = str(Node(node))
        self.assertEqual(exp, obs)
