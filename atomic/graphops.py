#!/usr/bin/env python3
"""
graphops
========

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


def filter(g, *args, **kwargs):
    """Filter nodes based on attributes.

    :arg ``newworkx.Graph`` g: Graph to operate upon.
    :arg ``Iterable`` args: List of attributes to return.
    :arg ``dict`` kwargs: Values to filter against. Presence of an attribute can
        be request by setting 'key=None', while non-None values will look for
        exact matches.
    """
    raise NotImplementedError()


def toplevel(g):
    """Return a list of top-level nodes; nodes without precessors."""
    return (n for n in g if is_toplevel(g, n))


def is_toplevel(g, n):
    """Does this node have predecessors?"""
    return not g.pred[n]
