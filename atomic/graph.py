#!/usr/bin/env python3
"""
graph
=====
"""
import enum
import json

from networkx.readwrite import json_graph


DEFAULT_FILENAME = '~/atomic.json'

# Edge Types
PARENT = "parent_of"
RELATED = "related_to"


def load(filename=DEFAULT_FILENAME):
    """Load the persisted :class:`networkx.MultiDiGraph`."""
    with open(filename) as f:
        data = json.load(f)
        return json_graph.node_link_graph(data, directed=True, multigraph=True)


def save(G, filename=DEFAULT_FILENAME):
    """Save the persisted :class:`networkx.MultiDiGraph`."""
    with open(filename) as f:
        data = json_graph.node_link_data(G)
        json.dump(data, f, indent=2)


def toplevel(g):
    """Return a list of top-level nodes; nodes without predecessors."""
    return (n for n in g if is_toplevel(g, n))


def is_toplevel(g, n):
    """Does this node have predecessors?"""
    return not g.pred[n]


class Node:
    """Nodes are the fundamental Graph primitive."""

    def __init__(self, uid, *args, **kwargs):
        self.uid = uid
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        return self.__dict__

    @classmethod
    def from_json(cls, json_object):
        return cls(**json_object)

    def __hash__(self, o):
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

    def __str__(self):
        return self.uid


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

"""
func vis(t tree) {
    if len(t) == 0 {
        fmt.Println("<empty>")
        return
    }
    var f func(int, string)
    f = func(n int, pre string) {
        ch := t[n].children
        if len(ch) == 0 {
            fmt.Println("╴", t[n].label)
            return
        }
        fmt.Println("┐", t[n].label)
        last := len(ch) - 1
        for _, ch := range ch[:last] {
            fmt.Print(pre, "├─")
            f(ch, pre+"│ ")
        }
        fmt.Print(pre, "└─")
        f(ch[last], pre+"  ")
    }
    f(0, "")
}
"""

class TreeParts(enum.Enum):
    parent = '┐'
    leaf = '-'
    child = '├─'
    last_child = '└─'
    bar = '|'
