#!/usr/bin/env python3
"""
graph
=====

Common operations I find myself performing on the graph backing Valence.
"""
import itertools

from collections import namedtuple


NodeDepth = namedtuple('NodeDepth', ['id', 'depth'])


def broad_dfs(g, depth=True):
    """Perform a depth-first search across all nodes, always beginning with
    nodes without predecessors.

    :return: A ``generator`` yielding an in-order sequence of nodes."""
    # All nodes without parents
    roots = (node for node in g if not g.pred[node])
    return itertools.chain.from_iterable((dfs(g, n, depth) for n in roots))


def dfs(g, n, depth=True):
    """Typical dfs, with customization provided through boolean options"""
    q = [NodeDepth(n, 0)]
    while q:
        u = q.pop()
        children = list(g.succ[u.id])  # dict => list
        if children:
            q.extend((NodeDepth(c, u.depth+1) for c in children[::-1]))
        if depth:
            yield u
        else:
            yield u.id
