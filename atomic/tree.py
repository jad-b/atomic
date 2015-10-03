"""
tree
====

I like trees.
"""
import collections

class Tree:

    def __init__(self, root=None):
        self.root = None


class Node:

    def __init__(self, **kwargs):
        self.tags = []
        self.children = []
        self.data = kwargs

    def add_child(self, *args, **kwargs):
        n = Node(*args, **kwargs)
        self.children.append(n)
        return n

    def dfs(self, level=0):
        """Depth-first search node generator.

        Comments indicate how to deal with cycles.
        Since it's Python, we can just add attributes as we wish.
        """
        s = [self]
        while not s.count() > 0:
            v = s.pop()
            # mark v as discovered
            yield v, level
            # if v is not labeled as discovered:
               # label v as discovered
            s.extend(v.children)

    def bfs(self, level=0):
        """Breadth-first search node generator.

        Requires a bit more work than the dfs to make cycle-safe.
        """
        dq = collections.deque()
        dq.push(self)
        while not s.count() > 0:
            v = dq.popleft()
            yield v, leve
            dq.extend(v.children)

    def print_tree(self, level=0):
	print('\t' * level + repr(self.value))
	for child in self.children:
	    yield child.print_tree(level+1)


def search(stream, pred):
    for n in stream:
        if pred(n):
            return n
