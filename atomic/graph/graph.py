#!/usr/bin/env python3
"""
graph
=====
Operations on the in-memory graph representation.
"""
import enum
from io import StringIO
from collections import deque

import networkx as nx


class EdgeTypes(enum.Enum):
    parent = "parent_of"
    related = "related_to"
    precedes = "precedes"


def toplevel(G):
    """Return a list of top-level nodes; nodes without predecessors."""
    return (n for n in G if not G.pred[n])


def hierarchy(G):
    """Produce child nodes in a depth-first order."""
    for root in toplevel(G):
        dq = deque()
        yield Node(root, **G.node[root]), len(dq)  # Depth 0
        # Iterate over all children
        dq.append(root)
        for src, dest in nx.dfs_edges(G, source=root):
            while len(dq) > 0 and dq[-1] != src:
                dq.pop()  # Unwind the stack
            if G.edge[src][dest].get('type') == EdgeTypes.PARENT:
                yield Node(dest, **G.node[dest]), len(dq)
            dq.append(dest)


class Node:
    """Nodes are the fundamental Graph primitive."""

    def __init__(self, uid: int, *args, **kwargs):
        self.uid = uid
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        return self.__dict__

    def __str__(self) -> str:
        sio = StringIO()
        header = '[{:d}] {:s}'.format(
            self.uid, getattr(self, 'name', '<No Name>'))
        sio.write('{}\n'.format(header))
        for k, v in self.__dict__.items():
            if k == 'name':
                continue
            sio.write('  {key}: {value}\n'.format(key=k, value=v))
        return sio.getvalue().rstrip('\n')

    def __repr__(self) -> str:
        return "{:d}) {:s}".format(self.uid,
                                   getattr(self, 'name', str(self.uid)))

    @classmethod
    def from_json(cls, json_object):
        return cls(**json_object)

    def __hash__(self):
        """Hash based off the UID."""
        return hash(self.uid)

    def __eq__(self, o):
        """Node's can compare to integers and other Node's.

        Integer comparison is off the assumption the integer reflects a uid.
        Node comparison assumes the Node's are within the same project, since
        Node's across projects can share unique identifiers.
        """
        if isinstance(o, int):
            return self.uid == o
        if isinstance(o, Node):
            return (self.uid == o.uid)
        raise NotImplemented


class Edge:

    def __init__(self, src, dst, _type, **kwargs):
        self.src = src
        self.dst = dst
        self._type = _type
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def from_json(cls, json_object):
        return cls(**json_object)


class Thought(Node):
    """Thoughts are recorded non-actionable ideas."""

    def __init__(self, *args, name=None, body=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.body = body

    def __str__(self):
        return self.name


class Action(Thought):
    """Actions are thoughts coupled with real-world events; your class Todo."""

    def __init__(self,
                 *args,
                 time_estd=None,
                 time_spent=None,
                 done=False,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.time_estd = time_estd
        self.time_spent = time_spent
        self.done = done
